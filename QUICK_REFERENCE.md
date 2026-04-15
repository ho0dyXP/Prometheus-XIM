# Prometheus-XIM Quick Reference

Handy lookup guide for the most common protocol information.

## 🚀 Quick Start (5 minutes)

```bash
# Install
pip install pyyaml winrt

# Test BLE sender
python tools/ble_sender.py --mode xbox --rate standard --dry-run

# Show hex
python tools/ble_sender.py --mode ps5 --rate 250 --show-hex --dry-run
```

## 📦 Packet Basics

| Property | Value |
|----------|-------|
| Type | 0x15 (config) |
| Subtype | 0x1D (settings commit) |
| Length | 0x64 (100 bytes) |
| Valid Range | 0x00–0x63 |

## 🎮 Input Modes (Offset 0x5E)

| Mode | Byte |
|------|------|
| Xbox/PC | 0x01 |
| PS5 | 0x02 |
| XInput | 0x03 |
| MnK | 0x04 |
| Hybrid | 0x05 |

## ⚡ Output Rates (Offset 0x5F)

| Rate | Byte | Hz |
|------|------|-----|
| Standard | 0x00 | ~16.7 |
| 250Hz | 0x01 | 250 |
| 500Hz | 0x02 | 500 |
| 1000Hz | 0x03 | 1000 |

**Note**: MnK & Hybrid modes force 0x03 (1000Hz)

## 🔗 Companion Codes (Offset 0x6D)

### By Mode & Rate

| Mode | Standard | 250Hz | 500Hz | 1000Hz |
|------|----------|-------|-------|--------|
| Xbox | 0x61 | 0xE8 | 0x23 | 0xF3 |
| PS5 | 0x15 | 0xE8 | 0x23 | 0xF3 |
| XInput | 0x31 | 0xE8 | 0x23 | 0xF3 |
| MnK | 0x32 (forced) | — | — | — |
| Hybrid | 0xF3 (forced) | — | — | — |

**Critical**: Fields 0x5E, 0x5F, 0x6D must update together!

## 🎯 Smart Action Modes (Offset 0x4F)

| Mode | Byte | Meaning |
|------|------|---------|
| Active | 0xC0 | Always on |
| Hip Only | 0xD0 | Hip-fire only |
| ADS Only | 0xE0 | Aim-down-sights only |
| Inactive | 0xF0 | Disabled |

## 🎨 Aim Curves (Offset 0x56–0x57)

| Preset | Signature |
|--------|-----------|
| Preset 1 | 0x06 0x0D |
| Preset 2 | 0x88 0x13 |
| Preset 3 | 0x06 0x0D |
| Preset 4 | 0x49 0x25 |
| Custom | (unknown) |

## 📋 Critical Offsets

| Offset | Size | Purpose |
|--------|------|---------|
| 0x00 | 1 | Type (0x15) |
| 0x01 | 1 | Subtype (0x1D) |
| 0x04–0x07 | 4 | Integrity (don't modify) |
| 0x4F | 1 | Smart action mode |
| 0x56–0x57 | 2 | Aim curve |
| 0x5E | 1 | **Input mode** |
| 0x5F | 1 | **Output rate** |
| 0x6D | 1 | **Companion code** |

## 🔁 Transaction Pattern

```
0x14 (8 bytes)   — Start
  ↓
0x15 (100 bytes) — CFG1D payload ← MAIN SETTINGS
  ↓
0x1D (8 bytes)   — Commit
  ↓
0x1E (12 bytes)  — Finalize (optional)
```

## ⚠️ Common Mistakes

❌ **Don't**:
- Modify integrity bytes (0x04–0x07)
- Change mode/rate without changing companion code
- Try to write past offset 0x63 (heap corruption)
- Use rate 0x01/0x02 with MnK or Hybrid modes

✅ **Do**:
- Update 0x5E, 0x5F, 0x6D atomically
- Validate packet length == 100 bytes
- Use rate 0x03 if mode is MnK or Hybrid
- Test with dry-run mode first

## 🔍 WinDbg Capture

```
Breakpoint: Windows_Devices_Bluetooth!GattCharacteristic::WriteValueInternal
Address:    0x00007fffe8ad08fc
Payload:    dd @rdx+0x50 L64  # Dump 100 bytes (0x64)
```

## 🧪 Test Commands

```bash
# Dry-run all 20 mode/rate combos
for mode in xbox ps5 xinput mnk hybrid; do
  for rate in standard 250 500 1000; do
    python tools/ble_sender.py --mode $mode --rate $rate --dry-run
  done
done

# Export to binary
python tools/ble_sender.py --mode xbox --rate standard --output config.bin

# Show complete hex dump
python tools/ble_sender.py --mode ps5 --rate 250 --show-hex --dry-run
```

## 📚 File Locations

| File | Purpose |
|------|---------|
| `reference/packet_reference.yaml` | Complete protocol mapping |
| `reference/MAPPING_CHECKLIST.yaml` | Features to map + strategy |
| `tools/ble_sender.py` | BLE packet sender |
| `docs/WINDBG_GUIDE.md` | Standardized WinDbg capture workflow |
| `examples/captures/CAPTURE_TEMPLATE.md` | Reusable per-session evidence template |
| `docs/README.md` | Documentation index |
| `CONTRIBUTING.md` | How to contribute |

## 🎓 Learning Path

1. Read this quick reference
2. Review `reference/packet_reference.yaml` (5 min)
3. Test `tools/ble_sender.py --dry-run` (2 min)
4. Explore `reference/MAPPING_CHECKLIST.yaml` (10 min)
5. Review `CONTRIBUTING.md` if contributing (5 min)
6. Start each capture session with `examples/captures/CAPTURE_TEMPLATE.md`
7. Check `docs/README.md` for deep dives (as needed)

## ❓ FAQ

**Q: What's the difference between rate tier and Hz?**
A: Rate tier (0x00–0x03) is what's sent in packet. Hz is the frequency interpretation. Standard=0x00≈16.7Hz, 1000Hz=0x03.

**Q: Why do MnK and Hybrid force 1000Hz?**
A: Hardware device limitation. These modes ignore user rate selection and always operate at maximum polling.

**Q: Can I modify aim curves?**
A: Yes, use 4 preset curves (fully mapped). Custom curve encoding is incomplete.

**Q: How do I capture my own packets?**
A: See `docs/WINDBG_GUIDE.md` (coming soon) or `reference/MAPPING_CHECKLIST.yaml` for capture strategy.

**Q: What's the companion code for?**
A: Synchronization/validation. Device rejects packets if companion code doesn't match mode/rate pair.

## 🚀 Next Steps

- **Beginner**: Run `ble_sender.py --mode xbox --rate standard --dry-run`
- **Developer**: Check WinRT integration TODO in code
- **Researcher**: Pick an unmapped feature from `MAPPING_CHECKLIST.yaml` and log captures in `examples/captures/`
- **Contributor**: Follow `CONTRIBUTING.md`

---

**Need more?** See `docs/README.md` for full documentation index.
