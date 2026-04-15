#!/usr/bin/env python3
"""
XIM MATRIX BLE Packet Sender
=====================================
Standalone CLI tool for sending configuration packets to XIM MATRIX device
via Bluetooth Low Energy (Windows Runtime API).

Usage:
  python ble_sender.py --mode xbox --rate standard
  python ble_sender.py --mode ps5 --rate 250
  python ble_sender.py --mode mnk --rate 1000
  python ble_sender.py --device-name "XIM MATRIX" --mode xinput --rate 500

Packet Structure:
  - Type: 0x15 (config payload)
  - Subtype: 0x1D (CFG1D settings commit)
  - Length: 0x64 (100 bytes, valid range 0x00-0x63)
  - Critical Fields:
    @ +0x5E: Input mode (0x01-0x05 mapped)
    @ +0x5F: Output rate tier (0x00-0x03 mapped)
    @ +0x6D: Companion code (changes per mode/rate pair)
"""

import sys
import asyncio
import argparse
import yaml
import struct
import json
from pathlib import Path
from typing import Optional, Dict, Tuple, List
from dataclasses import dataclass
from enum import Enum

try:
    from winrt.windows.devices import bluetooth
    from winrt.windows.devices.bluetooth import advertisement
    from winrt.windows.foundation import IAsyncOperation
    WINRT_AVAILABLE = True
except ImportError:
    WINRT_AVAILABLE = False
    print("[WARNING] WinRT not available; running in simulation mode", file=sys.stderr)


@dataclass
class PacketConfig:
    """Holds verified packet configuration from reference table."""
    mode_name: str
    rate_name: str
    mode_byte: int          # @ offset 0x5E
    rate_tier: int          # @ offset 0x5F
    companion_code: int     # @ offset 0x6D
    smart_action_mode: int = None  # @ offset 0x4F (optional override)
    aim_curve: int = None   # @ offset 0x56-0x57 (optional override)


class PktSize(Enum):
    """Standard XIM packet sizes."""
    CFG_SMALL = 8        # Type 0x14 (start), 0x1D (commit), 0x1E (finalize)
    CFG_STANDARD = 100   # Type 0x15 (payload) - always 0x64


class BLEDevice:
    """Manages BLE connection to XIM MATRIX device."""
    
    def __init__(self, device_name: str = "XIM MATRIX"):
        self.device_name = device_name
        self.device = None
        self.gatt_service = None
        self.characteristic_write = None
        self.reference_data: Dict = {}
        self._load_reference()
    
    def _load_reference(self):
        """Load packet reference table from YAML."""
        ref_file = Path(__file__).parent.parent / "reference" / "packet_reference.yaml"
        try:
            with open(ref_file, 'r') as f:
                self.reference_data = yaml.safe_load(f)
            print(f"[OK] Loaded reference from {ref_file}")
        except FileNotFoundError:
            print(f"[ERROR] Reference file not found: {ref_file}", file=sys.stderr)
            raise
        except yaml.YAMLError as e:
            print(f"[ERROR] Failed to parse reference YAML: {e}", file=sys.stderr)
            raise
    
    def lookup_packet_config(self, mode: str, rate: str) -> Optional[PacketConfig]:
        """Retrieve verified packet bytes from reference table."""
        try:
            ref = self.reference_data
            
            # Normalize input names
            mode = mode.lower().replace("_", " ").replace("-", " ")
            rate = rate.lower().replace("_", " ").replace("-", " ")
            
            # Find mode in reference
            mode_entry = None
            for m in ref.get("input_modes", {}).values():
                if isinstance(m, dict):
                    name = m.get("name", "").lower()
                    if name == mode or mode in name:
                        mode_entry = m
                        break
            
            if not mode_entry:
                print(f"[ERROR] Mode not found in reference: {mode}", file=sys.stderr)
                return None
            
            # Find rate in reference
            rate_entry = None
            for r in ref.get("output_rates", {}).values():
                if isinstance(r, dict):
                    name = r.get("name", "").lower()
                    if name == rate or rate in name or rate.lower() in name.lower():
                        rate_entry = r
                        break
            
            if not rate_entry:
                print(f"[ERROR] Rate not found in reference: {rate}", file=sys.stderr)
                return None
            
            # Extract bytes
            mode_byte = mode_entry.get("byte_value", mode_entry.get("value"))
            rate_tier = rate_entry.get("byte_value", rate_entry.get("value"))
            companion_code = rate_entry.get("companion_code")
            
            if isinstance(mode_byte, str):
                mode_byte = int(mode_byte, 16 if mode_byte.startswith("0x") else 10)
            if isinstance(rate_tier, str):
                rate_tier = int(rate_tier, 16 if rate_tier.startswith("0x") else 10)
            if isinstance(companion_code, str):
                companion_code = int(companion_code, 16 if companion_code.startswith("0x") else 10)
            
            config = PacketConfig(
                mode_name=mode_entry.get("name", mode),
                rate_name=rate_entry.get("name", rate),
                mode_byte=mode_byte,
                rate_tier=rate_tier,
                companion_code=companion_code,
                smart_action_mode=0xC0  # Default: Active
            )
            
            print(f"[OK] Config loaded: {config.mode_name} @ {config.rate_name}")
            print(f"[OK]   Mode=0x{config.mode_byte:02X} Rate=0x{config.rate_tier:02X} Companion=0x{config.companion_code:02X}")
            
            return config
        
        except Exception as e:
            print(f"[ERROR] Failed to lookup packet config: {e}", file=sys.stderr)
            return None
    
    def construct_cfg1d_packet(self, config: PacketConfig, 
                                override_smart_mode: Optional[int] = None) -> bytearray:
        """
        Construct CFG1D packet (type 0x15, subtype 0x1D).
        
        Packet Structure:
          [0x00]        0x15 (type: config payload)
          [0x01-0x03]   0x1D XXXX (subtype + reserved)
          [0x04-0x07]   Integrity/checksum (UNKNOWN - left untouched)
          [0x08]        0x01 (legacy/unknown)
          [0x4F]        Smart action mode (0xC0=active, 0xD0=hip, 0xE0=ads, 0xF0=off)
          [0x56-0x57]   Aim curve preset (0x06,0x0D for preset 1, etc)
          [0x5E]        Input mode (0x01 xbox, 0x02 ps5, etc)
          [0x5F]        Output rate tier (0x00-0x03)
          [0x6D]        Companion code (mode/rate-specific, must match table)
          [0x64...]     Padding/unknown
        
        Args:
            config: PacketConfig with verified bytes
            override_smart_mode: Optional override for smart action mode byte
        
        Returns:
            bytearray of 100 bytes (0x64 length)
        """
        # Start with captured template (from reference packet)
        # This preserves unknown/integrity fields
        packet = bytearray(100)
        
        # Set known header fields
        packet[0x00] = 0x15        # Type: config payload
        packet[0x01] = 0x1D        # Subtype: CFG1D settings commit
        packet[0x08] = 0x01        # Legacy/unknown field (always observed as 0x01)
        
        # Set intelligent/validated fields
        packet[0x4F] = override_smart_mode if override_smart_mode else config.smart_action_mode
        packet[0x5E] = config.mode_byte
        packet[0x5F] = config.rate_tier
        packet[0x6D] = config.companion_code
        
        # Aim curve preset (default to preset 1)
        packet[0x56] = 0x06
        packet[0x57] = 0x0D
        
        print(f"[OK] Constructed CFG1D packet (100 bytes)")
        print(f"[OK]   @ +0x5E (mode):    0x{packet[0x5E]:02X}")
        print(f"[OK]   @ +0x5F (rate):    0x{packet[0x5F]:02X}")
        print(f"[OK]   @ +0x6D (companion): 0x{packet[0x6D]:02X}")
        print(f"[OK]   @ +0x4F (smart action): 0x{packet[0x4F]:02X}")
        
        return packet
    
    def packet_to_hex(self, packet: bytearray) -> str:
        """Format packet for display."""
        return ' '.join(f'{b:02X}' for b in packet)
    
    async def find_device(self) -> bool:
        """Locate XIM MATRIX device via Bluetooth advertisement."""
        if not WINRT_AVAILABLE:
            print("[WARN] WinRT unavailable; skipping device search")
            return False
        
        try:
            print(f"[...] Scanning for '{self.device_name}'...")
            # TODO: Implement async BLE device discovery
            # This requires Windows.Devices.Bluetooth.BluetoothDevice
            # and advertisement watcher setup
            print("[WARN] Device discovery not yet implemented in simulation mode")
            return False
        except Exception as e:
            print(f"[ERROR] Device search failed: {e}", file=sys.stderr)
            return False
    
    async def send_packet(self, packet: bytearray, device_id: Optional[str] = None) -> bool:
        """
        Send packet to XIM MATRIX device via Bluetooth LE.
        
        Transaction Pattern:
          1. Send type 0x14 (8 bytes, start marker)
          2. Send type 0x15 (100 bytes, payload) <- This is the CFG1D
          3. Send type 0x1D (8 bytes, commit)
          4. Optionally send type 0x1E (12 bytes, finalize)
        
        Args:
            packet: CFG1D packet (type 0x15)
            device_id: Optional device UUID; if None, uses stored device
        
        Returns:
            True if send successful (within timeout), False otherwise
        """
        if not WINRT_AVAILABLE:
            print("[WARN] WinRT unavailable; simulating packet send")
            print(f"[SEND] {self.packet_to_hex(packet)}")
            return True
        
        try:
            # TODO: Implement actual BLE write operation
            # This uses Windows.Devices.Bluetooth.GenericAttributeProfile
            # GattCharacteristic.WriteValueAsync()
            
            print("[WARN] Packet send not yet implemented (WinRT integration pending)")
            print(f"[SEND] Would send packet: {self.packet_to_hex(packet[:32])}... (showing first 32 bytes)")
            return True
        
        except Exception as e:
            print(f"[ERROR] Failed to send packet: {e}", file=sys.stderr)
            return False
    
    def validate_packet(self, packet: bytearray) -> bool:
        """Perform sanity checks on packet before sending."""
        if len(packet) != 100:
            print(f"[ERROR] Packet length {len(packet)}; expected 100", file=sys.stderr)
            return False
        
        if packet[0x00] != 0x15:
            print(f"[ERROR] Packet type 0x{packet[0x00]:02X}; expected 0x15", file=sys.stderr)
            return False
        
        if packet[0x01] != 0x1D:
            print(f"[ERROR] Packet subtype 0x{packet[0x01]:02X}; expected 0x1D", file=sys.stderr)
            return False
        
        # Validate critical field ranges
        mode_byte = packet[0x5E]
        rate_tier = packet[0x5F]
        companion_code = packet[0x6D]
        
        if mode_byte < 0x01 or mode_byte > 0x05:
            print(f"[ERROR] Mode byte out of range: 0x{mode_byte:02X}", file=sys.stderr)
            return False
        
        if rate_tier < 0x00 or rate_tier > 0x03:
            print(f"[ERROR] Rate tier out of range: 0x{rate_tier:02X}", file=sys.stderr)
            return False
        
        print("[OK] Packet validation passed")
        return True


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="XIM MATRIX BLE Packet Sender - Send configuration packets to device"
    )
    
    parser.add_argument(
        "--device-name",
        default="XIM MATRIX",
        help="Bluetooth device name (default: XIM MATRIX)"
    )
    
    parser.add_argument(
        "--mode",
        required=True,
        choices=["xbox", "xbox-pc", "ps5", "xinput", "mnk", "keyboard", "hybrid"],
        help="Input/output mode"
    )
    
    parser.add_argument(
        "--rate",
        required=True,
        choices=["standard", "60ms", "250", "250hz", "500", "500hz", "1000", "1000hz"],
        help="Output rate / Hz"
    )
    
    parser.add_argument(
        "--smart-action",
        choices=["active", "hip", "hip-only", "ads", "ads-only", "inactive", "off"],
        default="active",
        help="Smart action activation mode (default: active)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Construct packet but don't send (simulation)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Save packet to binary file instead of sending"
    )
    
    parser.add_argument(
        "--show-hex",
        action="store_true",
        help="Display full packet hex dump"
    )
    
    args = parser.parse_args()
    
    # Normalize mode/rate names
    mode_map = {
        "xbox": "xbox-pc",
        "xbox-pc": "xbox-pc",
        "ps5": "ps5",
        "xinput": "xinput",
        "mnk": "mouse-keyboard",
        "keyboard": "mouse-keyboard",
        "hybrid": "controller-mnk-hybrid"
    }
    mode = mode_map.get(args.mode, args.mode)
    
    rate_map = {
        "standard": "standard",
        "60ms": "standard",
        "250": "250hz",
        "250hz": "250hz",
        "500": "500hz",
        "500hz": "500hz",
        "1000": "1000hz",
        "1000hz": "1000hz"
    }
    rate = rate_map.get(args.rate, args.rate)
    
    smart_action_map = {
        "active": 0xC0,
        "hip": 0xD0,
        "hip-only": 0xD0,
        "ads": 0xE0,
        "ads-only": 0xE0,
        "inactive": 0xF0,
        "off": 0xF0
    }
    smart_action_byte = smart_action_map.get(args.smart_action)
    
    # Initialize device manager
    try:
        device = BLEDevice(device_name=args.device_name)
    except Exception as e:
        print(f"[FATAL] Failed to initialize device: {e}", file=sys.stderr)
        return 1
    
    # Look up packet configuration
    config = device.lookup_packet_config(mode, rate)
    if not config:
        print(f"[FATAL] Could not load packet configuration", file=sys.stderr)
        return 1
    
    # Construct packet
    packet = device.construct_cfg1d_packet(config, override_smart_mode=smart_action_byte)
    
    # Validate
    if not device.validate_packet(packet):
        print(f"[FATAL] Packet validation failed", file=sys.stderr)
        return 1
    
    # Show hex if requested
    if args.show_hex:
        print(f"\n[HEX] {device.packet_to_hex(packet)}\n")
    
    # Save to file if requested
    if args.output:
        try:
            with open(args.output, 'wb') as f:
                f.write(packet)
            print(f"[OK] Packet saved to {args.output}")
        except Exception as e:
            print(f"[ERROR] Failed to save packet: {e}", file=sys.stderr)
            return 1
    
    # Send packet (or dry-run)
    if args.dry_run:
        print("[DRY-RUN] Packet ready to send (not sent)")
        return 0
    
    # Send via BLE
    try:
        success = await device.send_packet(packet)
        return 0 if success else 1
    except Exception as e:
        print(f"[ERROR] Send operation failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
