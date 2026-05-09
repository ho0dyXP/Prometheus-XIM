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
from uuid import UUID

XIM_MAC_ADDRESS  = "00:16:A4:DE:CD:6E"
XIM_SERVICE_UUID = "b7af0000-11d7-4d47-94ea-c7e255720093"
XIM_WRITE_UUID   = "b7af0001-11d7-4d47-94ea-c7e255720093"  # send packets here
XIM_NOTIFY_UUID  = "b7af0002-11d7-4d47-94ea-c7e255720093"  # listen for responses

try:
    from winrt.windows.devices import bluetooth  # pyright: ignore[reportMissingImports]
    from winrt.windows.devices.bluetooth import advertisement  # pyright: ignore[reportMissingImports]
    from winrt.windows.foundation import IAsyncOperation  # pyright: ignore[reportMissingImports]
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
    smart_action_mode: Optional[int] = None  # @ offset 0x4F (optional override)
    aim_curve: Optional[int] = None   # @ offset 0x56-0x57 (optional override)


class PktSize(Enum):
    """Standard XIM packet sizes."""
    CFG_SMALL = 8        # Type 0x14 (start), 0x1D (commit), 0x1E (finalize)
    CFG_STANDARD = 100   # Type 0x15 (payload) - always 0x64


class BLEDevice:
    """Manages BLE connection to XIM MATRIX device."""
    
    def __init__(self, device_name: str = "XIM MATRIX", device_mac: str = XIM_MAC_ADDRESS):
        self.device_name = device_name
        self.device_mac = device_mac
        self.device_address = self._parse_mac_address(device_mac)
        self.device = None
        self.gatt_service = None
        self.characteristic_write = None
        self.characteristic_notify = None
        self.reference_data: Dict = {}
        self._load_reference()

    def _parse_mac_address(self, mac_address: str) -> int:
        """Convert a MAC string like 00:16:A4:DE:CD:6E into a Bluetooth address integer."""
        return int(mac_address.replace(":", "").replace("-", ""), 16)
    
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

    def _normalize_name(self, value: str) -> str:
        return value.lower().replace("_", " ").replace("-", " ")

    def _coerce_int_value(self, value: object) -> Optional[int]:
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            return int(value, 16 if value.startswith("0x") else 10)
        return None

    def _find_reference_entry(self, entries: Dict, query: str) -> Optional[Dict]:
        normalized_query = self._normalize_name(query)
        for entry in entries.values():
            if isinstance(entry, dict):
                name = self._normalize_name(entry.get("name", ""))
                if name == normalized_query or normalized_query in name:
                    return entry
        return None
    
    def lookup_packet_config(self, mode: str, rate: str) -> Optional[PacketConfig]:
        """Retrieve verified packet bytes from reference table."""
        try:
            ref = self.reference_data
            mode_entry = self._find_reference_entry(ref.get("input_modes", {}), mode)
            if not mode_entry:
                print(f"[ERROR] Mode not found in reference: {mode}", file=sys.stderr)
                return None

            rate_entry = self._find_reference_entry(ref.get("output_rates", {}), rate)
            if not rate_entry:
                print(f"[ERROR] Rate not found in reference: {rate}", file=sys.stderr)
                return None

            mode_byte = self._coerce_int_value(mode_entry.get("byte_value", mode_entry.get("value")))
            rate_tier = self._coerce_int_value(rate_entry.get("byte_value", rate_entry.get("value")))
            companion_code = self._coerce_int_value(rate_entry.get("companion_code"))

            if mode_byte is None or rate_tier is None or companion_code is None:
                print(f"[ERROR] Incomplete packet reference for mode={mode} rate={rate}", file=sys.stderr)
                return None
            
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
        packet[0x4F] = override_smart_mode if override_smart_mode is not None else (config.smart_action_mode or 0xC0)
        packet[0x5E] = config.mode_byte
        packet[0x5F] = config.rate_tier
        packet[0x6D] = config.companion_code
        
        # Aim curve preset (default to preset 1)
        packet[0x56] = 0x06
        packet[0x57] = 0x0D
        
        print("[OK] Constructed CFG1D packet (100 bytes)")
        print(f"[OK]   @ +0x5E (mode):    0x{packet[0x5E]:02X}")
        print(f"[OK]   @ +0x5F (rate):    0x{packet[0x5F]:02X}")
        print(f"[OK]   @ +0x6D (companion): 0x{packet[0x6D]:02X}")
        print(f"[OK]   @ +0x4F (smart action): 0x{packet[0x4F]:02X}")
        
        return packet
    
    def packet_to_hex(self, packet: bytearray) -> str:
        """Format packet for display."""
        return ' '.join(f'{b:02X}' for b in packet)
    
    async def find_device(self) -> bool:
        """Compatibility wrapper that resolves the device through the direct MAC connection path."""
        if not WINRT_AVAILABLE:
            print("[WARN] WinRT unavailable; skipping device search")
            return False
        
        try:
            print(f"[...] Connecting directly to '{self.device_name}' at MAC {self.device_mac}...")
            return await self.connect()
        except Exception as e:
            print(f"[ERROR] Device search failed: {e}", file=sys.stderr)
            return False

    async def connect(self) -> bool:
        """Connect directly to the device by MAC address and resolve GATT handles."""
        if not WINRT_AVAILABLE:
            print("[WARN] WinRT unavailable; skipping BLE connection")
            return False

        try:
            if self.device is None:
                print(f"[...] Connecting directly to MAC {self.device_mac}")
                from winrt.windows.devices import bluetooth as bluetooth_module  # pyright: ignore[reportMissingImports]
                self.device = await bluetooth_module.BluetoothLEDevice.from_bluetooth_address_async(self.device_address)

            if not self.device:
                print(f"[ERROR] Could not connect to device at MAC {self.device_mac}", file=sys.stderr)
                return False

            services_result = await self.device.get_gatt_services_for_uuid_async(UUID(XIM_SERVICE_UUID))
            if not services_result.services:
                print(f"[ERROR] Service not found: {XIM_SERVICE_UUID}", file=sys.stderr)
                return False

            self.gatt_service = services_result.services[0]

            write_result = await self.gatt_service.get_characteristics_for_uuid_async(UUID(XIM_WRITE_UUID))
            if not write_result.characteristics:
                print(f"[ERROR] Write characteristic not found: {XIM_WRITE_UUID}", file=sys.stderr)
                return False

            self.characteristic_write = write_result.characteristics[0]

            notify_result = await self.gatt_service.get_characteristics_for_uuid_async(UUID(XIM_NOTIFY_UUID))
            if notify_result.characteristics:
                self.characteristic_notify = notify_result.characteristics[0]

            print(f"[OK] Connected to {self.device_mac}")
            print(f"[OK]   Service: {XIM_SERVICE_UUID}")
            print(f"[OK]   Write:   {XIM_WRITE_UUID}")
            print(f"[OK]   Notify:  {XIM_NOTIFY_UUID}")
            return True

        except Exception as e:
            print(f"[ERROR] BLE connection failed: {e}", file=sys.stderr)
            return False

    async def connect_persistent(self) -> bool:
        """Establish and keep a cached WinRT connection for repeated sends."""
        if self.device and self.gatt_service and self.characteristic_write:
            return True
        return await self.connect()

    def disconnect(self) -> None:
        """Release the cached WinRT device handle."""
        self.characteristic_notify = None
        self.characteristic_write = None
        self.gatt_service = None
        self.device = None

    async def send_packet_fast(self, packet: bytearray) -> bool:
        """Hot path: use warm connection and only cold-start when needed."""
        if self.characteristic_write is None:
            if not await self.connect_persistent():
                return False
        return await self.send_packet(packet)
    
    async def send_packet(self, packet: bytearray) -> bool:
        """
        Send packet to XIM MATRIX device via Bluetooth LE.
        
        Transaction Pattern:
          1. Send type 0x14 (8 bytes, start marker)
          2. Send type 0x15 (100 bytes, payload) <- This is the CFG1D
          3. Send type 0x1D (8 bytes, commit)
          4. Optionally send type 0x1E (12 bytes, finalize)
        
        Args:
            packet: CFG1D packet (type 0x15)
        Returns:
            True if send successful (within timeout), False otherwise
        """
        if self.device is None or self.characteristic_write is None:
            if not await self.connect():
                return False
        
        try:
            characteristic_write = self.characteristic_write
            if characteristic_write is None:
                return False

            from winrt.windows.storage.streams import DataWriter  # pyright: ignore[reportMissingImports]

            async def write_payload(payload: bytearray) -> None:
                writer = DataWriter()
                writer.write_bytes(payload)
                await characteristic_write.write_value_async(writer.detach_buffer())

            # Step 1: Start marker (0x14, 8 bytes)
            start = bytearray(8)
            start[0] = 0x14
            await write_payload(start)
            print("[OK] Sent start marker (0x14)")

            # Step 2: CFG1D payload (0x15, 100 bytes)
            await write_payload(packet)
            print("[OK] Sent CFG1D payload (0x15)")

            # Step 3: Commit (0x1D, 8 bytes)
            commit = bytearray(8)
            commit[0] = 0x1D
            await write_payload(commit)
            print("[OK] Sent commit (0x1D)")

            # Step 4: Finalize (0x1E, 12 bytes)
            finalize = bytearray(12)
            finalize[0] = 0x1E
            await write_payload(finalize)
            print("[OK] Sent finalize (0x1E)")
            print("[OK] Transaction complete")
            return True
        
        except Exception as e:
            print(f"[ERROR] Failed to send packet: {e}", file=sys.stderr)
            self.disconnect()
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
        "--device-mac",
        default=XIM_MAC_ADDRESS,
        help=f"Bluetooth MAC address (default: {XIM_MAC_ADDRESS})"
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

    if not mode or not rate:
        print("[FATAL] Missing required CLI arguments", file=sys.stderr)
        return 1
    
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
        device = BLEDevice(device_name=args.device_name, device_mac=args.device_mac)
    except Exception as e:
        print(f"[FATAL] Failed to initialize device: {e}", file=sys.stderr)
        return 1
    
    # Look up packet configuration
    config = device.lookup_packet_config(mode, rate)
    if not config:
        print("[FATAL] Could not load packet configuration", file=sys.stderr)
        return 1
    
    # Construct packet
    packet = device.construct_cfg1d_packet(config, override_smart_mode=smart_action_byte)
    
    # Validate
    if not device.validate_packet(packet):
        print("[FATAL] Packet validation failed", file=sys.stderr)
        return 1
    
    # Show hex if requested
    if args.show_hex:
        print(f"\n[HEX] {device.packet_to_hex(packet)}\n")
    
    # Save to file if requested
    if args.output:
        try:
            await asyncio.to_thread(Path(args.output).write_bytes, packet)
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
