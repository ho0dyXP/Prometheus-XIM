# Project Documentation Guide

Welcome to the Prometheus-XIM documentation structure. This directory contains comprehensive guides, technical deep-dives, and research notes.

## 📖 Documentation Files

### Getting Started
- **[README.md](../README.md)** — Project overview, quick start, and navigation

### Reference & Protocol
- **[packet_reference.yaml](../reference/packet_reference.yaml)** — Complete packet structure mapping (source of truth)
- **[MAPPING_CHECKLIST.yaml](../reference/MAPPING_CHECKLIST.yaml)** — Feature inventory and capture strategy guide

### Technical Guides
- **[WINDBG_GUIDE.md](WINDBG_GUIDE.md)** — Step-by-step WinDbg packet capture methodology
- **[PROTOCOL_DEEP_DIVE.md](PROTOCOL_DEEP_DIVE.md)** *(To be created)* — Detailed technical analysis of packet structures
- **[ARCHITECTURE.md](ARCHITECTURE.md)** *(To be created)* — Design decisions, trade-offs, and rationale

### Tools & Usage
- **[BLE_SENDER_USAGE.md](BLE_SENDER_USAGE.md)** *(To be created)* — How to use the BLE sender tool
- **[../examples/captures/README.md](../examples/captures/README.md)** — Durable capture archive workflow and templates

### Contribution
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** — How to contribute findings and improvements

## 🧭 How to Navigate

**I want to...**

**...understand what this project does:**
→ Start with [README.md](../README.md)

**...see the complete protocol mapping:**
→ Read [packet_reference.yaml](../reference/packet_reference.yaml)

**...find what features still need mapping:**
→ Check [MAPPING_CHECKLIST.yaml](../reference/MAPPING_CHECKLIST.yaml)

**...capture new packets using WinDbg:**
→ Follow [WINDBG_GUIDE.md](WINDBG_GUIDE.md)

**...avoid losing capture progress between sessions:**
→ Use [../examples/captures/README.md](../examples/captures/README.md)

**...understand WHY we chose the BLE sender architecture:**
→ Read [ARCHITECTURE.md](ARCHITECTURE.md) (coming soon)

**...learn all packet byte offsets and meanings:**
→ Study [PROTOCOL_DEEP_DIVE.md](PROTOCOL_DEEP_DIVE.md) (coming soon)

**...use the BLE sender tool:**
→ See [BLE_SENDER_USAGE.md](BLE_SENDER_USAGE.md) and tool --help

**...contribute my findings:**
→ Read [CONTRIBUTING.md](../CONTRIBUTING.md)

## 📚 Content Status

| Document | Status | Content |
|----------|--------|---------|
| README.md | ✓ Complete | Project overview, quick start |
| packet_reference.yaml | ✓ Complete | All protocol mappings |
| MAPPING_CHECKLIST.yaml | ✓ Complete | Feature inventory |
| WINDBG_GUIDE.md | ✓ Complete | Capture methodology and logging workflow |
| PROTOCOL_DEEP_DIVE.md | 🟡 Planned | Technical analysis |
| ARCHITECTURE.md | 🟡 Planned | Design rationale |
| BLE_SENDER_USAGE.md | 🟡 Planned | Tool documentation |
| examples/captures/README.md | ✓ Complete | Session archive + template workflow |

## 🔍 Key Concepts

### Packet Structure
The XIM MATRIX uses Bluetooth LE packets to configure device behavior. The main packet type is:
- **CFG1D** (type 0x15, subtype 0x1D): 100-byte settings payload
- See [packet_reference.yaml](../reference/packet_reference.yaml) for complete byte-level breakdown

### Protocol Discovery
We use **WinDbg packet interception** to discover protocol structures:
1. Set breakpoint at Bluetooth write function
2. Perform single setting change
3. Capture resulting packet
4. Compare against baseline to identify byte changes
5. Document findings in reference tables

### Current Status
- ✓ 20/20 mode/rate combinations verified
- ◐ 9/70 features partially mapped
- ○ 56/70 features pending investigation
- ⏳ Velocity calibration blocked on hardware availability

## 🛠️ Tools

- **ble_sender.py** — CLI tool for packet construction and transmission
- WinDbg — For packet capture and analysis
- Python 3.8+ — Script language
- PyYAML — For configuration management

## 🎯 Next Steps

1. **For Explorers**: Read README.md then packet_reference.yaml
2. **For Contributors**: Read CONTRIBUTING.md then pick a feature from MAPPING_CHECKLIST.yaml
3. **For Developers**: Explore tools/ble_sender.py and plan WinRT integration
4. **For Researchers**: Review existing captures in examples/ and protocol documentation

## 📞 Getting Help

- **General Questions**: GitHub Discussions
- **Bugs/Issues**: GitHub Issues
- **Contribute Findings**: See CONTRIBUTING.md
- **Technical Discussion**: GitHub Discussions (Technical category)

---

**Last Updated**: April 2026  
**Documentation Version**: 1.0  
**Contributors**: See project commit history
