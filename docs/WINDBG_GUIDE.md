# WinDbg Capture Guide

This guide standardizes XIM MATRIX packet capture so findings are reproducible and easy to recover later.

## Goals

- Capture full BLE write packets for a single UI setting change.
- Persist logs to files so findings survive editor or chat history loss.
- Produce structured notes that can be merged into `reference/MAPPING_CHECKLIST.yaml`.

## Prerequisites

- Windows 10/11
- WinDbg (Preview recommended)
- XIM Manager app running and connected to device
- Repo checked out locally

## Session Durability Workflow (Important)

Always do these steps at session start:

1. Create a timestamped notes file from `examples/captures/CAPTURE_TEMPLATE.md`.
2. Enable WinDbg file logging with `.logopen /t`.
3. Save all packet dumps into the same notes file before ending session.
4. Commit or copy the notes file to cloud storage after each session.

This avoids losing progress when IDE updates clear conversation history.

## Recommended Folder Convention

- Session notes: `examples/captures/YYYY-MM-DD_session-N.md`
- Raw debugger logs: `examples/captures/raw/YYYY-MM-DD_session-N_windbg.log`
- Packet diffs: inline in the session note under a dedicated heading

## Target Breakpoint

Use symbol-based breakpoint first (preferred):

```text
x Windows_Devices_Bluetooth!*WriteValueInternal*
bu Windows_Devices_Bluetooth!GattCharacteristic::WriteValueInternal
```

If symbols fail, use known absolute address only for the current build:

```text
bp 0x00007fffe8ad08fc
```

## Packet Fields at Breakpoint

At `GattCharacteristic::WriteValueInternal`:

- Payload pointer: `poi(@rdx+0x50)`
- Payload length: `poi(@rdx+0x58)` (or `dd @rdx+0x58 L1`)

For CFG1D, expected packet length is `0x64` (100 bytes).

## One-Setting Capture Procedure

1. Launch WinDbg attached to target process used by the app path that triggers BLE writes.
2. Set breakpoint and continue.
3. In app UI, change exactly one setting once.
4. When breakpoint hits, record:
   - timestamp
   - setting changed
   - packet type/subtype
   - full hex dump
5. Repeat with a second value for the same setting (min/max is ideal).
6. Diff the two dumps to isolate changing bytes.

## WinDbg Command Block

Paste this block after attaching:

```text
.symfix
.reload
.logopen /t c:\tmp\Prometheus-XIM\examples\captures\raw\windbg_session.log
x Windows_Devices_Bluetooth!*WriteValueInternal*
bu Windows_Devices_Bluetooth!GattCharacteristic::WriteValueInternal
g
```

When hit, run:

```text
r rdx
? poi(@rdx+0x50)
? @rdx+0x58
dd @rdx+0x58 L1
db poi(@rdx+0x50) L100
```

Optional filtered check (CFG1D heuristic):

```text
db poi(@rdx+0x50) L2
```

Expected:

- `+0x00 = 0x15`
- `+0x01 = 0x1D`

Then continue:

```text
g
```

At end of session:

```text
.logclose
```

## Capture Quality Checklist

- Single setting changed per capture
- Full 100-byte dump saved (no truncation)
- Baseline and modified values both captured
- At least 2 repeat captures for reproducibility
- Offsets and interpretation recorded in session note

## Suggested High-Priority Capture Order

1. Hip Sensitivity X then Y
2. ADS Sensitivity X then Y
3. Hip Aim Curve preset sweep (Preset 1-4, then Custom baseline)
4. ADS Aim Curve preset sweep (Preset 1-4, then Custom baseline)
5. Custom curve point move test (single-point drag, Hip then ADS)
6. Input source selection (mouse/controller/keyboard)
7. Button remap basic swap
8. Single Smart Action payload (auto-fire)

## Curve Capture Micro-Protocol

Use this sequence for both Hip and ADS to keep curve evidence comparable:

1. Enter curve editor and record context (Hip or ADS).
2. Capture Preset 1, 2, 3, 4 using button index left-to-right.
3. Switch to Custom and capture untouched linear baseline.
4. Move exactly one control point once and capture.
5. Move a different point once and capture.

Custom tool mode mapping (left to right):

- Tool 1: free handle/control-point drag.
- Tool 2: square/flat segment shaping.
- Tool 3: linearize selected points.
- Tool 4: remove curve handles.

Notes:

- Do not combine point moves in one capture.
- Do not switch tool modes and move points in the same capture.
- Keep sensitivity values fixed while mapping curves.
- Keep activation/delay unchanged during curve captures.

## Minimal-Sufficient Curve Matrix (Recommended)

You do not need to move every point in every direction.

Use this minimal set to finish mapping with high confidence:

1. Baseline: Preset 4 in ADS, then baseline in Hip.
2. Tool 1: one endpoint drag (to boundary) and one interior-point left/right drag.
3. Tool 2: one square/flat edit on one interior point.
4. Tool 3: one linearize action on one interior point.
5. Tool 4: one remove-handle action with a clear before/after.
6. Repeat steps 2-5 once in the other context (ADS or Hip) for schema parity.

Stop criteria:

- Same byte regions respond consistently across ADS and Hip.
- Tool-specific behavior is repeatable in at least one mirrored context run.
- No new offset regions appear in two consecutive captures.

When stop criteria are met, prioritize interpretation over additional capture volume.

Fallback when one-step drags are too hard:

- Use repeatable anchor moves instead of tiny drags:
   - endpoint Y `0 -> 100`
   - endpoint Y `100 -> 0`
- Capture baseline before each anchor move, then capture immediately after the move.
- If possible, do the reverse move as a second capture pair to confirm symmetry.
- Add a short note in session evidence like `coarse move used` so diffs are interpreted correctly.

## Notes on Known Risks

- Do not infer meaning from one capture only.
- Preserve integrity region bytes (`0x04-0x07`) as observed.
- Avoid assumptions when packet type/length differs from CFG1D.

## How to Promote Findings

After verification:

1. Add result to your session file in `examples/captures/`.
2. Update status and evidence notes in `reference/MAPPING_CHECKLIST.yaml`.
3. If field semantics are confirmed, update `reference/packet_reference.yaml`.
4. Open PR with raw evidence and interpreted mapping.



