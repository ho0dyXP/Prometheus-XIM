# Capture Session Template

## Session Metadata

- Date:
- Session ID:
- Analyst:
- XIM firmware:
- Firmware seen in log (optional):
- App version:
- Host OS:
- WinDbg version:


## Objective

- Feature to map:
- Priority:
- Expected packet type:

## Rapid Window Card (Copy/Paste Per Movement)

Use this for fast iterative mapping windows.

```text
Window ID: H-T1-W01
Context: Hip|ADS  Tool: T1|T2|T3|T4
Baseline preset: 4 (reset)
Action intent: <one action only>
Action detail: start=<point/anchor>; target=<intended destination>; actual=<where it ended>
Mishap: no|yes (<short note if yes>)
Start marker: first packet after last `g`
Packets included: primary only | primary+companion
Expected region: <known tuple region or unknown>
```

Notes:
- If baseline is Preset 4, treat as a fresh reference window.
- If a mishap occurred, keep the window but mark it `Mishap: yes` so it is excluded from canonical comparisons unless later reproduced.
- Prefer one save for baseline and one save for action window to keep attribution clean.

## Breakpoint Setup

- Symbol breakpoint used:
- Fallback address used (if any):
- Logging file path:

## Baseline Capture

- UI value:
- Hit timestamp:
- Length observed:
- Full hex dump:

```text
PASTE_BASELINE_HEX_HERE
```

## Modified Capture

- UI value:
- Hit timestamp:
- Length observed:
- Full hex dump:

```text
PASTE_MODIFIED_HEX_HERE
```

## Diff Analysis

- Changed offsets:
- Old bytes -> new bytes:
- Candidate encoding:
- Confidence level (low/medium/high):

## Reproducibility

- Repeat run count:
- Same offsets repeated: yes/no
- Edge values tested:

## Conclusion

- Proposed mapping:
- Packet type/subtype:
- Validation status:
- Next action:

## Raw Log Link

- WinDbg log file:
