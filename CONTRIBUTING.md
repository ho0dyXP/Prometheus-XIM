# Contributing to Prometheus-XIM

Thank you for your interest in contributing to the XIM MATRIX protocol reverse-engineering project! This document explains how you can help us map the device's Bluetooth protocol and improve the tooling.

## 🎯 Ways to Contribute

### 1. **Packet Capture & Documentation**
The most valuable contribution is discovering new protocol structures via WinDbg.

**How to contribute a finding:**
1. Follow the WinDbg capture methodology in `docs/WINDBG_GUIDE.md`
2. Select an unmapped feature from `reference/MAPPING_CHECKLIST.yaml`
3. Perform single-setting captures and document results
4. Submit findings with:
   - Raw packet hex dumps
   - Before/after comparison
   - Setting value changed
   - Byte offset(s) affected
5. Create a pull request updating `reference/MAPPING_CHECKLIST.yaml` with status

**Example contribution format:**
```yaml
finding:
  feature: "Hip Sensitivity X"
  date: "2026-04-15"
  contributor: "[Your Name]"
  captured_offset: "0x68"
  byte_changes: "0x68-0x6B: [0x00, 0x00, 0x80, 0x3F] → [0x00, 0x00, 0x80, 0x40]"
  interpretation: "IEEE 754 float pair; base 1.0 changed to 1.0000000"
  tested: true
  status: "verified"
```

### 2. **Code Improvements**
Help complete the BLE sender tool and add features.

**Priority areas:**
- WinRT Bluetooth LE integration (device discovery, packet transmission)
- Error handling and validation
- Configuration file parsing
- unit tests
- Documentation

**Code style:**
- Python 3.8+ compatible
- PEP 8 compliant  
- Type hints where practical
- Docstrings for all functions
- Comments for complex logic

### 3. **Documentation**
Improve guides, examples, and protocol documentation.

- Found a bug in the docs? Submit a correction
- Have a clearer explanation? Propose an update
- Created a useful example? Share it
- Spotted a typo? Fix it!

### 4. **Testing & Validation**
- Test packet generation with different hardware
- Verify captures across different XIM firmware versions
- Test BLE sender against actual devices
- Report edge cases and failures

### 5. **Community Resources**
- Share gaming configuration templates in `configs/`
- Create detailed capture examples in `examples/`
- Write tutorials for using the tools
- Help other contributors with captures

## 📋 Submission Process

### Step 1: Pick a Task
Browse `reference/MAPPING_CHECKLIST.yaml` and choose:
- An unmapped feature from Phase 2-4
- A code improvement from `TODO` comments
- A documentation gap you noticed

### Step 2: Create Findings File
If documenting a protocol discovery:

```bash
# Create a findings document
mkdir -p submitted_findings
touch submitted_findings/your_feature_finding.md
```

**Template:**
```markdown
# Finding: [Feature Name]

## Basic Info
- **Feature**: Hip Sensitivity X Mapping
- **Contributor**: [Your Name]
- **Date**: 2026-04-15
- **XIM Firmware**: [Version if known]

## Capture Methodology
1. Set Hip Sensitivity to minimum (0.1x)
2. Intercept at GattCharacteristic::WriteValueInternal
3. Captured packet: [hex dump]
4. Repeated with maximum (10x)
5. Captured packet: [hex dump]

## Findings
- **Offset**: 0x68-0x6B
- **Byte Changes**: 
  - Min: 0x00 0x00 0x80 0x3F (1.0 in IEEE 754)
  - Max: 0x00 0x00 0x80 0x43 (8.0 in IEEE 754)
- **Encoding**: IEEE 754 single-precision float
- **Conclusion**: 4-byte float multiplier @ offset 0x68

## Verification
- Tested: Yes
- Reproducible: Yes (multiple independent captures)
- Edge cases tested: Yes (middle values, boundary conditions)
```

### Step 3: Submit via Pull Request

```bash
# Fork the repo
git clone https://github.com/YOUR_FORK/Prometheus-XIM.git
cd Prometheus-XIM

# Create feature branch
git checkout -b feature/your-finding-name

# Make your changes
# Update reference/MAPPING_CHECKLIST.yaml with new status
# Add any code improvements

# Commit with descriptive message
git commit -m "Map [Feature Name]: [Brief description]

- Discovered offset 0x68-0x6B contains IEEE 754 float
- 4-byte hip sensitivity X multiplier
- Tested across range 0.1x-10x
- Updated MAPPING_CHECKLIST with Phase 2 finding"

# Push to your fork
git push origin feature/your-finding-name

# Open pull request on main repo
```

### Step 4: Code Review
- Maintainers will review your submission
- May ask for additional testing or clarification
- Merge once approved

## 🏆 Attribution & Credits

All contributors are:
- **Named** in commits and pull requests
- **Listed** in project CONTRIBUTORS file
- **Credited** in feature documentation
- **Recognized** in release notes

## 💡 Tips for Effective Contributions

### WinDbg Captures
- Capture **single changes** (one setting per session)
- **Document baseline** (default config) for comparison
- Use **sequence numbers** to track packet ordering
- Save **full 100-byte dumps** (not truncated)
- Repeat captures **multiple times** for verification

### Code Contributions
- **Test locally** before submitting
- **Add comments** for non-obvious logic
- **Keep PRs focused** (one feature per PR)
- **Reference issues** in commit messages
- **Update docs** if changing behavior

### Documentation
- Use **clear, technical language**
- Include **concrete examples**
- Add **code samples** for complex concepts
- Link to **relevant sections** of documentation
- Fix **typos and clarity issues**

## 🤔 Questions?

- **Protocol questions**: Post in GitHub Discussions
- **Tool problems**: Open a GitHub Issue with:
  - Your OS and Python version
  - Error message (full stack trace)
  - Steps to reproduce
  - Expected vs actual behavior
- **Capture help**: See `docs/WINDBG_GUIDE.md` or ask in Discussions

## 📚 Resources

- **WinDbg Capture Guide**: `docs/WINDBG_GUIDE.md`
- **Protocol Reference**: `reference/packet_reference.yaml`
- **Feature Checklist**: `reference/MAPPING_CHECKLIST.yaml`
- **Code Examples**: `examples/` directory
- **Architecture**: `docs/ARCHITECTURE.md`

## ⚠️ Contribution Guidelines

### Do's ✅
- Contribute legitimate gaming optimization findings
- Use WinDbg capture methodology for packet discovery
- Reference official XIM documentation where applicable
- Be respectful and collaborative
- Test thoroughly before submitting
- Document your work clearly

### Don'ts ❌
- Don't submit packet captures from private/patented systems
- Don't attempt to reverse-engineer authentication or copy protection
- Don't submit low-quality findings without verification
- Don't include credentials or sensitive information
- Don't violate game ToS or legal boundaries

## 🔐 Security & Legal

**This project is for legitimate purposes:**
- XIM MATRIX is officially supported by Xbox, PS5, and PC
- Reverse-engineering public protocol structures is legal research
- We use only packet structure analysis (black-box methodology)
- No exploitation of vulnerabilities or circumvention of protections

**Before contributing, ensure:**
- Your finding doesn't violate game ToS
- You're following local laws regarding device modification
- You have authorization for any hardware/software you're analyzing
- You're not leaking confidential or proprietary information

## 🎉 Thank You!

Every contribution—no matter how small—helps the community better understand and optimize gaming on XIM MATRIX devices. We appreciate your effort and look forward to working with you!

---

**Questions about contributing?** Open a GitHub Discussion or issue!
