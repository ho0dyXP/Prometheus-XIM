# Capture Session: Hip Sensitivity Delta (Preliminary)

## Metadata
- Date: 2026-04-14
- Feature: Hip Sensitivity adjustment (+/- 1 step)
- Packet path: GattCharacteristic::WriteValueInternal
- Observed packet variant: type=0x15, subtype=0x00, len=0x64

## Packet A
```text
15 00 79 00 27 fd 74 cf 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e4 02 e4 02 00 00
00 00 00 00 00 00 06 0d 00 00 10 27 10 27 ff ff
ff ff ff ff
```

## Packet B
```text
15 00 7c 00 b9 f2 2b 4c 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 da 02 da 02 00 00
00 00 00 00 00 00 06 0d 00 00 10 27 10 27 ff ff
ff ff ff ff
```

## Diff (A -> B)
- 0x02: 0x79 -> 0x7C
- 0x04: 0x27 -> 0xB9
- 0x05: 0xFD -> 0xF2
- 0x06: 0x74 -> 0x2B
- 0x07: 0xCF -> 0x4C
- 0x4A: 0xE4 -> 0xDA
- 0x4C: 0xE4 -> 0xDA

## Preliminary Interpretation
- 0x02 likely sequence/version counter (non-semantic drift).
- 0x04-0x07 likely integrity/check field.
- 0x4A and 0x4C are strong candidates for sensitivity-linked values.
- Mirrored change at 0x4A and 0x4C suggests paired axis/state representation.

## Verification Plan
1. Capture three controlled points for Hip value: N, N+1, N+2.
2. Confirm monotonic movement at 0x4A/0x4C with fixed deltas.
3. Repeat for ADS to check whether same offsets or a second pair is used.
4. Record whether subtype remains 0x00 for this flow consistently.

## Status
- Confidence: Medium (needs one more capture step for numeric scaling)
- Suitable to annotate as "candidate offsets" in mapping checklist.

## Additional Captures (Same Session)

### Packet C (Subtype 0x00, hip variant)
```text
15 00 82 00 4f b4 bf 97 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e4 02 e4 02 00 00
00 00 00 00 00 00 06 0d 00 00 10 27 10 27 ff ff
ff ff ff ff
```

### Packet D (Subtype 0x00, hip variant)
```text
15 00 85 00 65 76 94 dc 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 da 02 da 02 00 00
00 00 00 00 00 00 06 0d 00 00 10 27 10 27 ff ff
ff ff ff ff
```

### Packet E (Custom curve mode selected)
```text
15 00 88 00 04 d3 2f 73 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 da 02 da 02 01 00
00 00 00 00 00 00 06 0d 00 00 10 27 10 27 ff ff
ff ff ff ff
```

## Refined Interpretation
- Sensitivity candidate remains strongest at 0x4A and 0x4C (e4 <-> da observed repeatedly).
- 0x02 increments across saves and appears sequence-like.
- 0x04-0x07 remain volatile and appear integrity/session-linked.
- Switching to custom curve mode toggled 0x4E from 0x00 to 0x01 while preserving 0x4A/0x4C pattern.
- Packet subtype 0x00 is confirmed for this firmware/app save path.

## UI Evidence: Curve Editor Present In ADS

- Screenshot evidence confirms the same Curve Editor is available under ADS (header shows "Stick: ADS").
- ADS editor exposes the same four preset buttons shown in the lower row of the editor UI.
- ADS custom mode allows direct graph manipulation by dragging control points/handles, matching Hip behavior.
- This validates that curve mapping must be captured per-context (Hip and ADS), not assumed shared only from one section.

### Preset Button Visual Classes (left to right)
- Preset 1: near-linear/diagonal baseline.
- Preset 2: gentle convex rise.
- Preset 3: stronger late acceleration shape.
- Preset 4: aggressive multi-handle curve (S-like mid section with steep upper-end ramp).

### Custom Curve Tool Buttons (left to right)
- Tool 1: free handle/control-point manipulation (drag handles and points directly).
- Tool 2: add/select point and square off for flat-gain style segments (near right-angle transitions).
- Tool 3: convert selected points/segments toward linear behavior.
- Tool 4: remove curve handles.

Latest screenshot update:
- User-confirmed "last preset" corresponds to Preset 4 (rightmost button).
- ADS graph shows a compressed late-stage ramp with clustered upper-right control handles, consistent with aggressive acceleration behavior.

These labels are for capture indexing only; packet-level semantics still require per-preset WinDbg evidence.

## ADS Curve Preset Capture Set (All ADS Sensitivity Context)

Context:
- Captures were taken under ADS curve editor flow with ADS sensitivity fields held at X=1.0 (`0x000A`) and Y=0.9 (`0x0009`).
- First-chance `80000003` events occurred between captures and are expected debugger breaks.

### Preset Capture A (user-labeled Preset 1)
```text
15 00 e9 00 c5 c0 0f 0c 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 09 00 01 00 00 00 00 00 00 00
06 0d 00 00 10 27 10 27 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff
```

### Preset Capture B (user-labeled Preset 2)
```text
15 00 e5 00 ba 43 1f cc 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 09 00 01 00 00 00 00 00 00 00
88 13 88 13 10 27 10 27 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff
```

### Preset Capture C (user-labeled Preset 3)
```text
15 00 d6 00 70 77 7d 74 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 09 00 01 00 00 00 00 00 00 00
49 25 1b 0a 03 26 22 0d d5 26 7e 0f 10 27 10 27
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff
```

### Preset Capture D (user-labeled Preset 4 / last preset)
```text
15 00 e1 00 6c 76 26 d1 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 09 00 01 00 00 00 00 00 00 00
3f 12 54 06 ca 12 3b 08 57 13 69 09 7a 13 98 0e
e0 13 d6 13 64 14 6b 14 fa 14 99 15 00 1d e5 17
83 25 98 1a
```

### Continuation/Companion Packet Observed With Preset D
```text
15 00 e2 00 da 2c 72 85 08 00 00 00 05 26 76 1c
9d 26 07 1e 10 27 10 27 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00
```

### ADS Curve Interpretation Update
- ADS curve data is confirmed to serialize in packets where sensitivity fields remain fixed (`0x34/0x36 = 0x000A/0x0009`), isolating curve behavior from sensitivity changes.
- Known signatures reappear in ADS context:
	- `06 0d 00 00`
	- `88 13 88 13`
- Additional ADS captures show longer point-table style payloads in the same curve region, especially for user-labeled Preset 4 (last preset), and can emit a companion packet.
- This indicates curve presets are not always represented by a single 4-byte signature in this flow; some presets/shapes serialize as extended curve data.

## HIP Curve Preset Sequence (User-Labeled Order, Crash/Restart Interruption)

User-labeled order for this run:
- Preset 1
- Preset 2
- Preset 3
- Application crash/restart
- Preset 4

### HIP Sequence Capture 1 (user-labeled Preset 1)
```text
15 00 d6 00 70 77 7d 74 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 09 00 01 00 00 00 00 00 00 00
49 25 1b 0a 03 26 22 0d d5 26 7e 0f 10 27 10 27
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff
```

### HIP Sequence Capture 2 (user-labeled Preset 2)
```text
15 00 d9 00 50 dd 53 82 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 09 00 01 00 00 00 00 00 00 00
3f 12 54 06 ca 12 3b 08 57 13 69 09 7a 13 98 0e
e0 13 d6 13 64 14 6b 14 fa 14 99 15 00 1d e5 17
83 25 98 1a
```

### HIP Sequence Capture 3 (user-labeled Preset 3 companion/extended packet)
```text
15 00 da 00 e6 87 07 d6 08 00 00 00 05 26 76 1c
9d 26 07 1e 10 27 10 27 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00
```

### Crash/Restart Telemetry Observed
- `Communication lost`
- `Windows Runtime Originate Error - code 40080201` (repeated first-chance)
- `Transport Disconnected` / reconnect scan / `Transport Connected`
- Session resumed on firmware `7.00.20260323`

### Post-Restart Preset Captures (includes user-labeled Preset 4)
- `15 00 dd ... 88 13 88 13 ...`
- `15 00 e1 ... 3f 12 54 06 ... 83 25 98 1a`
- `15 00 e5 ... 88 13 88 13 ...`
- `15 00 e9 ... 06 0d 00 00 ...`
- `15 00 f4 ... 49 25 1b 0a 03 26 22 0d d5 26 7e 0f ...`

### Interpretation (HIP Curve Ordering)
- In this run, signature families appear in the user-labeled order but not with a one-to-one stable mapping against prior assumed preset indices.
- Crash/restart introduces additional transport/session packets and duplicate signature emissions, which can reorder or replay preset-associated payloads.
- Treat this run as high-value evidence for curve payload families, but not as final index lock for Preset 1/2/3/4 mapping.

## Curve Preset Sweep (Clean No-Restart: Hip 1->4, then ADS 1->4)

Run conditions:
- No application restart during preset sweep.
- Sensitivity fields remained stable during curve transitions (`0x000A` / `0x0009` in ADS-context packets, `0x02E3` / `0x03DF` in Hip-context packets).

### Recurring Preset Families Observed In Order
- Family A: `88 13 88 13` (short signature form)
- Family B: `06 0D 00 00` (short signature form)
- Family C: starts `49 25 1B 0A 03 26 22 0D ...` (extended form)
- Family D: starts `3F 12 54 06 CA 12 3B 08 ...` (extended form)

### Primary Packets (By User-Stated Selection Order)
- Hip Preset 1: Family A
- Hip Preset 2: Family B
- Hip Preset 3: Family C
- Hip Preset 4: Family D
- ADS Preset 1: Family A
- ADS Preset 2: Family B
- ADS Preset 3: Family C
- ADS Preset 4: Family D

### Companion Packets
- Extended families can emit companion packets (`... 04/08 ...`) that carry continuation data or table tails.
- Companion packets should be tied to the nearest prior primary preset packet in the same context.

### Interpretation Update
- This clean run removes restart-replay ambiguity and supports a consistent left-to-right preset family order in both Hip and ADS.
- Preset mapping should now be treated as provisionally locked to families A->D above, with remaining work focused on custom point editing semantics.

## ADS Custom Curve Point Drag Test (Starting From Preset 1)

User action sequence:
- Start from Preset 1 (linear baseline family).
- Drag lower-left endpoint from Y=0.0 to Y=100.0.
- Drag upper-right endpoint from Y=100.0 down to Y=0.0.
- Final screenshot shows both endpoints moved (inverted-style endpoint arrangement).

### Captured Packets (ADS context)

Packet CUST-1
```text
15 00 55 01 1a 99 de 43 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 09 00 01 00 00 00 00 00 00 00
88 13 00 00 10 27 00 00 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff
```

Packet CUST-2
```text
15 00 58 01 10 9b ab 62 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 09 00 01 00 00 00 00 00 00 00
88 13 10 27 10 27 10 27 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff
```

Packet CUST-3
```text
15 00 5b 01 06 b3 93 5b 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 09 00 01 00 00 00 00 00 00 00
88 13 0f 1d 10 27 10 27 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff
```

Packet CUST-4
```text
15 00 5e 01 61 14 ab bf 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 09 00 01 00 00 00 00 00 00 00
88 13 26 1e 10 27 10 27 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff
```

Packet CUST-5
```text
15 00 61 01 3e 75 1c 10 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 09 00 01 00 00 00 00 00 10 27
88 13 10 27 10 27 10 27 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff
```

Packet CUST-6
```text
15 00 64 01 66 4d 58 a6 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 09 00 01 00 00 00 00 00 10 27
88 13 00 00 10 27 00 00 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff
```

### Candidate Encoding Observations (ADS Custom)
- Sensitivity fields remained fixed at `0x34/0x36 = 0x000A/0x0009`, isolating custom-curve edits.
- Curve-region bytes changed primarily at:
	- `0x42/0x43` (observed `0000`, `1D0F`, `1E26`, `2710`)
	- `0x46/0x47` (observed `0000` and `2710`)
	- `0x3E/0x3F` (observed toggle to `2710` in later packets)
- `0x2710` appears to encode curve-domain 100.0 endpoint value.
- This strongly suggests uint16 fixed-point endpoint/control values in a 0..10000 domain for curve editor coordinates.

## ADS Custom Tool 1 Test (Preset 4, Top-Right Endpoint Drag)

User-provided setup:
- Starting preset: Preset 4.
- Starting selected point readout: `x=0.499`, `y=0.278`.
- Tool mode: Tool 1 (free handle/control-point drag).
- Action: drag top-right-most point to opposite bottom-right corner.
- End readout from screenshot: `x=1.000`, `y=0.000`.

### Packet TOOL1-P4-A (pre/near-start)
```text
15 00 34 02 12 0f 38 37 08 00 00 00 05 26 76 1c
9d 26 24 1e 10 27 10 27 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00
```

### Packet TOOL1-P4-B (post-drag)
```text
15 00 37 02 d3 93 d2 35 08 00 00 00 05 26 76 1c
9d 26 00 00 10 27 00 00 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00
```

### Delta Notes (TOOL1-P4-A -> TOOL1-P4-B)
- In the subtype `0x08` point-table header region:
  - `0x12/0x13`: `24 1E` -> `00 00`
  - `0x16/0x17`: `10 27` -> `00 00`
  - `0x14/0x15` stayed `10 27`.
- This is consistent with forcing selected point components toward zero while preserving one anchor component at max (`0x2710`).
- These packets strengthen the hypothesis that this front table (`0x0C+`) carries active curve-point coordinates for custom edits.

## ADS Custom Tool 2 Test (Preset 4, Square/Flat Segment Edit)

User-provided setup:
- Reset curve to Preset 4.
- Starting selected point readout: `x=0.664`, `y=0.064`.
- Tool mode: Tool 2 (square/flat segment shaping).
- Action: drag selected point vertically to `x=0.490`, `y=1.000`.

### Packet TOOL2-P4-A (baseline preset-4)
```text
15 00 43 02 4d e2 c6 4e 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 09 00 01 00 00 00 00 00 00 00
3f 12 54 06 ca 12 3b 08 57 13 69 09 7a 13 98 0e
e0 13 d6 13 64 14 6b 14 fa 14 99 15 00 1d e5 17
83 25 98 1a
```

### Packet TOOL2-P4-B (first post-edit)
```text
15 00 46 02 7d 40 82 ca 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 09 00 01 00 00 00 00 00 00 00
3f 12 54 06 ca 12 3b 08 5c 13 10 27 7a 13 98 0e
e0 13 d6 13 64 14 6b 14 fa 14 99 15 00 1d e5 17
83 25 98 1a
```

### Packet TOOL2-P4-C (refined post-edit)
```text
15 00 49 02 c4 65 82 f1 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 09 00 01 00 00 00 00 00 00 00
3f 12 54 06 ca 12 3b 08 20 13 10 27 7a 13 98 0e
e0 13 d6 13 64 14 6b 14 fa 14 99 15 00 1d e5 17
83 25 98 1a
```

### Delta Notes (TOOL2-P4-A -> TOOL2-P4-C)
- Sensitivity bytes remain fixed at `0x34/0x36 = 0x000A/0x0009`.
- Stable changes are concentrated in the mid tuple of the extended curve family:
	- `... 57 13 69 09 7A 13 ...` (baseline)
	- `... 20 13 10 27 7A 13 ...` (post-edit)
- `0x2710` insertion in the second value of that tuple matches the reported move to `y=1.000`.
- The neighboring first value shifted from `0x1357` to `0x1320`, consistent with x-position update while y hit max.
- This strongly suggests Tool 2 modifies a selected coordinate pair inside the extended point-table rather than only endpoint header bytes.

## ADS Custom Tool 3 Test (Preset 4, Linearize Selected Points)

User clarification:
- This run was Tool 3 (third option in the row), not Tool 2.
- Image 2 is the starting point for this sequence.

### Packet TOOL3-P4-A (starting baseline)
```text
15 00 76 02 d0 88 20 a5 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 09 00 01 00 00 00 00 00 00 00
3f 12 54 06 ca 12 3b 08 57 13 69 09 7a 13 98 0e
e0 13 d6 13 64 14 6b 14 fa 14 99 15 00 1d e5 17
83 25 98 1a
```

### Packet TOOL3-P4-B (companion/transition)
```text
15 00 77 02 d2 1f 00 39 08 00 00 00 05 26 76 1c
9d 26 07 1e 10 27 10 27 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00
```

### Packet TOOL3-P4-C (edited state)
```text
15 00 7a 02 42 3b 6b 05 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 09 00 01 00 00 00 00 00 00 00
3f 12 54 06 ca 12 3b 08 57 13 69 09 7a 13 98 0e
e0 13 d6 13 64 14 6b 14 34 15 99 15 3a 1d e5 17
bd 25 98 1a
```

### Packet TOOL3-P4-D (stronger linearized state)
```text
15 00 7d 02 83 f6 8c 43 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 09 00 01 00 00 00 00 00 00 00
3f 12 54 06 ca 12 3b 08 57 13 69 09 7a 13 98 0e
e0 13 d6 13 64 14 6b 14 eb 14 00 00 f1 1c 00 00
b5 24 00 00
```

### Packet TOOL3-P4-E (reset back to preset baseline)
```text
15 00 80 02 19 00 78 45 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 09 00 01 00 00 00 00 00 00 00
3f 12 54 06 ca 12 3b 08 57 13 69 09 7a 13 98 0e
e0 13 d6 13 64 14 6b 14 fa 14 99 15 00 1d e5 17
83 25 98 1a
```

### Delta Notes (TOOL3-P4-A -> TOOL3-P4-D)
- Sensitivity bytes stay fixed (`0x34/0x36 = 0x000A/0x0009`), isolating curve-tool effects.
- Early extended tuple block (`...3f 12 54 06 ca 12 3b 08 57 13 69 09 7a 13 98 0e...`) remains unchanged.
- Changes concentrate in the later extended tuple block beginning near `...64 14 6b 14 ...`:
	- baseline: `fa 14 99 15 00 1d e5 17 83 25 98 1a`
	- edited:   `34 15 99 15 3a 1d e5 17 bd 25 98 1a`
	- stronger: `eb 14 00 00 f1 1c 00 00 b5 24 00 00`
- Several paired fields are forced to `0x0000` in the stronger state, consistent with Tool 3 linearization behavior collapsing handle components.

## ADS Custom Tool 4 Test (Preset 4, Remove-Handle Mode)

User clarification:
- Tool mode was Tool 4 (remove handles).
- Direction correction: dragged to the right (not left).
- Image 1 indicates baseline point selection; Image 2 indicates end state.

### Packet TOOL4-P4-A (baseline preset-4)
```text
15 00 96 02 61 22 87 33 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 09 00 01 00 00 00 00 00 00 00
3f 12 54 06 ca 12 3b 08 57 13 69 09 7a 13 98 0e
e0 13 d6 13 64 14 6b 14 fa 14 99 15 00 1d e5 17
83 25 98 1a
```

### Packet TOOL4-P4-B (transition companion)
```text
15 00 97 02 63 b5 a7 af 08 00 00 00 05 26 76 1c
9d 26 07 1e 10 27 10 27 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00
```

### Packets TOOL4-P4-C..F (edited trajectory)
- `15 00 9a ... 64 14 6b 14 51 15 99 15 57 1d e5 17 da 25 98 1a`
- `15 00 9d ... 64 14 6b 14 28 17 5c 15 2e 1f a9 17 05 26 5c 1a`
- `15 00 a0 ... 64 14 6b 14 37 1f b2 15 05 26 00 18 05 26 b3 1a`
- `15 00 a3 ... 64 14 6b 14 a3 1e b2 15 71 25 00 18 05 26 b3 1a`

### Delta Notes (TOOL4-P4-A -> TOOL4-P4-F)
- Sensitivity bytes remain fixed (`0x34/0x36 = 0x000A/0x0009`).
- Early tuple region remains stable through the run.
- Late tuple region after `...64 14 6b 14...` changes substantially, with monotonic-like shifts in multiple fields as the selected control is dragged rightward.
- Intermittent `0x0000` values appear in paired fields in later packets, consistent with handle removal/simplification behavior interacting with control-point movement.

## ADS Custom Tool 1 Test (Preset 4, Bottom-Left Drag Saturation)

User-provided setup:
- Tool mode: Tool 1 (free point movement).
- Baseline preset: Preset 4.
- Action: grab bottom-left control and drag cursor across to the opposite side.
- Observed UI behavior: selected point stopped around middle even while cursor continued moving.

### Packet TOOL1-P4-BL-1 (captured changed state)
15 00 a9 02 a9 6e 86 43 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 09 00 01 00 00 00 00 00 4f 00
3f 12 0e 02 ca 12 3b 08 57 13 69 09 7a 13 98 0e
e0 13 d6 13 64 14 6b 14 fa 14 99 15 00 1d e5 17
83 25 98 1a

### Delta Notes (vs Preset 4 baseline)
- Sensitivity bytes remain fixed (`0x34/0x36 = 0x000A/0x0009`).
- Candidate movement-state byte changed from `0x0000` to `0x004F` in the pre-tuple area.
- Early extended tuple changed from `3f 12 54 06 ...` to `3f 12 0e 02 ...` while neighboring tuple anchors remained stable.
- This pattern is consistent with Tool 1 applying a bounded/clamped coordinate update for that selected control point rather than allowing unconstrained traversal across the full graph.

## ADS Custom Tool 1 Test (Second Point Drag Left)

User-provided setup:
- Tool mode: Tool 1 (free point movement).
- Baseline context: Preset 4, cursor on the next point in the curve (second point).
- Action: drag selected point left.
- Image 2 corresponds to end state.

### Packet TOOL1-P4-SP-L-A (starting state)
```text
15 00 af 02 ee 73 59 03 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 09 00 01 00 00 00 00 00 00 00
5c 12 53 06 e7 12 3a 08 74 13 68 09 7a 13 98 0e
e0 13 d6 13 64 14 6b 14 fa 14 99 15 00 1d e5 17
83 25 98 1a
```

### Packet TOOL1-P4-SP-L-B (post left-drag)
```text
15 00 b2 02 a0 ba c2 35 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 09 00 01 00 00 00 00 00 00 00
00 00 9c 06 00 00 83 08 63 06 b1 09 7a 13 98 0e
e0 13 d6 13 64 14 6b 14 fa 14 99 15 00 1d e5 17
83 25 98 1a
```

### Delta Notes (TOOL1-P4-SP-L-A -> TOOL1-P4-SP-L-B)
- Sensitivity bytes remain fixed (`0x34/0x36 = 0x000A/0x0009`).
- Changes are concentrated in early/mid extended tuple values tied to the selected point neighborhood:
	- `5c 12 53 06 e7 12 3a 08 74 13 68 09`
	- became
	- `00 00 9c 06 00 00 83 08 63 06 b1 09`
- Later tuple region (`...7a 13 98 0e e0 13 d6 13 64 14 6b 14 fa 14 99 15 00 1d e5 17 83 25 98 1a`) remained stable in this pair.
- This indicates Tool 1 left-drag on that selected point rewrites a local tuple segment while preserving downstream anchors, consistent with localized control-point editing.

## ADS Custom Tool 1 Final Mixed-Point Run (Closure Sample)

User-provided run context:
- Start from Preset 4 baseline.
- First grab: middle point intended left-drag.
- Observed behavior: point resisted pure left movement and shifted upward/slightly left (constraint-like behavior).
- Without resetting baseline, second grab: different middle point moved right.
- Entire sequence captured as one continuous dump set.

### Packet TOOL1-MIX-A (first grab result)
```text
15 00 b8 02 a3 a5 c6 c6 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 09 00 01 00 00 00 00 00 00 00
3f 12 54 06 ca 12 3b 08 57 13 69 09 7a 13 98 0e
e0 13 d6 13 64 14 6b 14 64 14 ba 18 00 1d e5 17
83 25 98 1a
```

### Packet TOOL1-MIX-B (second grab result, same run)
```text
15 00 bb 02 8a ca c1 52 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 09 00 01 00 00 00 00 00 00 00
3f 12 54 06 ca 12 3b 08 57 13 69 09 7a 13 98 0e
c4 1c 00 13 c4 1c 94 13 e2 1c df 17 00 1d e5 17
83 25 98 1a
```

### Delta Notes (TOOL1-MIX-A -> TOOL1-MIX-B)
- Sensitivity fields remain fixed (`0x34/0x36 = 0x000A/0x0009`).
- Early tuple block stays stable (`3f 12 54 06 ca 12 3b 08 57 13 69 09 7a 13 98 0e`).
- Edits are confined to the late tuple block (beginning near prior `...e0 13 d6 13 64 14 6b 14 ...`).
- No new packet address region emerged; direction and selection alter values inside already-known curve tuple zones.

### Closure Interpretation
- This mixed run reinforces the core conclusion from earlier directional testing:
	- left/right and up/down edits share the same structural tuple regions;
	- movement direction and UI constraints change value transitions, not packet layout family.
- Suitable as final ADS directional/control-behavior evidence for this phase.

## HIP Custom Tool 1 Mirror (Bottom-Left Endpoint Upward Drag)

User-provided setup:
- Context: Hip curve editor.
- Baseline: Preset 4.
- Tool mode: Tool 1 (free point movement).
- Action: move bottom-left point upward toward top edge (matching prior ADS endpoint-style test).

### Packet HIP-TOOL1-EP-A (baseline-like state)
```text
15 00 c0 02 ea 86 54 9b 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e3 02 df 03 01 00
00 00 00 00 00 00 3f 12 53 06 ca 12 3b 08 57 13
69 09 7a 13
```

### Packet HIP-TOOL1-EP-B (post-drag)
```text
15 00 c3 02 89 17 16 c2 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e3 02 df 03 01 00
00 00 00 00 10 27 3f 12 10 27 ca 12 3b 08 57 13
69 09 7a 13
```

### Delta Notes (HIP-TOOL1-EP-A -> HIP-TOOL1-EP-B)
- Hip sensitivity fields remain fixed (`0x4A/0x4C = 0x02E3/0x03DF`), isolating curve behavior.
- New `0x2710` values are injected into the early tuple neighborhood (`... 10 27 ... 10 27 ...`), indicating max-bound coordinate assignment during endpoint move.
- Remaining tuple tail (`...3b 08 57 13 69 09 7a 13`) stays stable.

### Cross-Context Interpretation
- This mirrors ADS behavior where Tool 1 endpoint drags inject boundary values while preserving other tuple anchors.
- Supports shared curve schema between ADS and Hip with context-specific sensitivity fields but consistent tuple semantics.

## HIP Custom Tool 1 Mirror (Interior Point, Left Attempt With Constraint)

User-provided setup:
- Context: Hip curve editor.
- Baseline: Preset 4.
- Tool mode: Tool 1.
- Intended action: drag selected interior point left.
- Observed behavior: point moved upward (constraint-like), then was moved back down.

### Packet HIP-TOOL1-IP-A
```text
15 00 e4 02 f8 41 a8 59 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e3 02 df 03 01 00
00 00 00 00 00 00 3f 12 54 06 ca 12 3b 08 64 14
08 23 64 14
```

### Packet HIP-TOOL1-IP-B (companion)
```text
15 00 e5 02 e9 b6 29 fd 04 00 00 00 10 27 64 14
10 27 64 14 6b 14 fa 14 99 15 00 1d e5 17 83 25
98 1a 05 26 76 1c 9d 26 07 1e 10 27 10 27 ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 98 3a 64 00 00 00 e8 03
0a 00 14 5a
```

### Packet HIP-TOOL1-IP-C
```text
15 00 e8 02 d6 1e 3e b3 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e3 02 df 03 01 00
00 00 00 00 00 00 3f 12 54 06 ca 12 3b 08 0a 14
00 00 0a 14
```

### Packet HIP-TOOL1-IP-D (companion)
```text
15 00 e9 02 94 35 61 b3 04 00 00 00 00 00 27 14
00 00 64 14 6b 14 fa 14 99 15 00 1d e5 17 83 25
98 1a 05 26 76 1c 9d 26 07 1e 10 27 10 27 ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 98 3a 64 00 00 00 e8 03
0a 00 14 5a
```

### Packet HIP-TOOL1-IP-E
```text
15 00 ec 02 0c 31 88 2b 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e3 02 df 03 01 00
00 00 00 00 00 00 3f 12 54 06 ca 12 3b 08 76 13
00 00 76 13
```

### Packet HIP-TOOL1-IP-F (companion)
```text
15 00 ed 02 32 c4 97 51 04 00 00 00 00 00 0a 14
00 00 64 14 6b 14 fa 14 99 15 00 1d e5 17 83 25
98 1a 05 26 76 1c 9d 26 07 1e 10 27 10 27 ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 98 3a 64 00 00 00 e8 03
0a 00 14 5a
```

### Delta Interpretation
- Hip sensitivity bytes remained fixed (`0x4A/0x4C = 0x02E3/0x03DF`) through the sequence.
- The same early tuple neighborhood changed repeatedly (`...3b 08 XX XX ...`) while core anchors remained stable.
- Companion packets (`type 0x04`) carried continuation/state chunks matching the edited point trajectory.
- Behavior mirrors ADS constrained motion: attempted leftward drag can be projected into allowed movement paths while still updating known tuple regions.

## HIP Custom Tool 1 Mirror (Point Left From Baseline)

User-provided setup:
- Tool mode: Tool 1 (free point movement).
- Baseline: Preset 4.
- Action: drag selected point left.

### Packet HIP-TOOL1-L-A (baseline state)
```text
15 00 fd 02 d4 e4 b2 58 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e3 02 df 03 01 00
00 00 00 00 00 00 5c 12 53 06 e7 12 3a 08 74 13
68 09 7a 13
```

### Packet HIP-TOOL1-L-B (post left-drag)
```text
15 00 00 03 80 5a bd 25 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e3 02 df 03 01 00
00 00 00 00 00 00 00 00 9d 0e 00 00 9d 0e 00 00
4a 0f 7a 13
```

### Delta Notes (HIP-TOOL1-L-A -> HIP-TOOL1-L-B)
- Hip sensitivity bytes remain fixed (`0x4A/0x4C = 0x02E3/0x03DF`).
- Selected local tuple neighborhood is rewritten from:
	- `5c 12 53 06 e7 12 3a 08 74 13 68 09`
	- to
	- `00 00 9d 0e 00 00 9d 0e 00 00 4a 0f`
- Final anchor `7a 13` remains stable.
- This mirrors ADS local rewrite behavior for Tool 1 left-drags and further supports shared tuple schema.
- Repeat run later in session produced the same rewrite signature, reinforcing reproducibility for Hip Tool1 left-drag behavior.

## HIP Custom Tool 1 Mirror (Boundary Wall Then Upward Move, Last-g Window)

User clarification:
- Scope: only packets from the last `g` onward (fresh movement window).
- Baseline: Preset 4.
- Action: attempted left drag into boundary wall, then moved up.

### Packet HIP-TOOL1-BND-A (primary)
```text
15 00 2e 03 01 07 22 33 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e3 02 df 03 01 00
00 00 00 00 00 00 3f 12 54 06 ca 12 3b 08 ca 12
69 09 ca 12
```

### Packet HIP-TOOL1-BND-B (companion)
```text
15 00 2f 03 9e 8c fb 23 04 00 00 00 98 0e ca 12
d6 13 64 14 6b 14 fa 14 99 15 00 1d e5 17 83 25
98 1a 05 26 76 1c 9d 26 07 1e 10 27 10 27 ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 98 3a 64 00 00 00 e8 03
0a 00 14 5a
```

### Packet HIP-TOOL1-BND-C (primary)
```text
15 00 32 03 db d4 4c 8a 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e3 02 df 03 01 00
00 00 00 00 00 00 3f 12 54 06 ca 12 3b 08 ca 12
6b 20 74 13
```

### Packet HIP-TOOL1-BND-D (companion)
```text
15 00 33 03 45 06 24 b7 04 00 00 00 9a 25 92 13
10 27 64 14 6b 14 fa 14 99 15 00 1d e5 17 83 25
98 1a 05 26 76 1c 9d 26 07 1e 10 27 10 27 ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 98 3a 64 00 00 00 e8 03
0a 00 14 5a
```

### Delta Notes (HIP-TOOL1-BND-A/B -> HIP-TOOL1-BND-C/D)
- Sensitivity bytes stayed fixed at `0x4A/0x4C = 0x02E3/0x03DF`.
- The same Tool1 tuple neighborhood changed again (late part of primary payload):
	- `... 3b 08 ca 12 69 09 ca 12`
	- to
	- `... 3b 08 ca 12 6b 20 74 13`
- Companion payload head shifted from `98 0e ca 12 ...` to `9a 25 92 13 ...`, consistent with boundary-conditioned movement and then upward relocation.
- This supports the same conclusion as prior Tool1 runs: movement direction/state changes values, but packet family/layout region stays stable.

## HIP Tool3 Candidate (H-T3-W01, Middle Point Right-Wall Then Down Then Top)

User-provided flow:
- Baseline: Preset 4.
- Starting point: middle point selected.
- Action path: attempted move right (hit boundary), then moved straight down, then to top.
- UI state in screenshot indicates Tool3 linearize mode during this window.

### Packet H-T3-W01-A (baseline primary)
```text
15 00 42 03 e4 36 29 b3 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e3 02 df 03 01 00
00 00 00 00 00 00 3f 12 54 06 ca 12 3b 08 57 13
69 09 7a 13
```

### Packet H-T3-W01-B (baseline companion)
```text
15 00 43 03 e2 2c ab 7d 04 00 00 00 98 0e e0 13
d6 13 64 14 6b 14 fa 14 99 15 00 1d e5 17 83 25
98 1a 05 26 76 1c 9d 26 07 1e 10 27 10 27 ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 98 3a 64 00 00 00 e8 03
0a 00 14 5a
```

### Packet H-T3-W01-C (post-action primary)
```text
15 00 46 03 be 29 41 30 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e3 02 df 03 01 00
00 00 00 00 00 00 7a 13 35 06 7a 13 1c 08 7a 13
4a 09 7a 13
```

### Packet H-T3-W01-D (post-action primary)
```text
15 00 49 03 29 47 1a c7 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e3 02 df 03 01 00
00 00 00 00 00 00 7a 13 00 00 7a 13 00 00 7a 13
00 00 7a 13
```

### Packet H-T3-W01-E (post-action primary)
```text
15 00 4c 03 2b 40 f4 77 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e3 02 df 03 01 00
00 00 00 00 00 00 f4 11 10 27 f4 11 10 27 12 12
10 27 7a 13
```

### Delta Interpretation
- Sensitivity bytes stayed fixed at `0x4A/0x4C = 0x02E3/0x03DF`.
- Primary payload family and rewrite region stayed consistent with prior curve edits (late tuple block), while values changed aggressively across the three post-action packets.
- Intermediate state `...7a 13 00 00 7a 13 00 00 7a 13 00 00 7a 13` indicates temporary clamp/degenerate tuple geometry during boundary-conditioned movement.
- Final state includes multiple `0x2710` values (`10 27`) consistent with top-bound saturation behavior in curve-domain coordinates.
- This is usable as a representative Hip Tool3 boundary-path sample, but confidence is tagged mixed-action because multiple path steps occurred in one window.

## HIP Tool3 Repeat (H-T3-W02, Constrained Slight Down-Angle)

User-provided flow:
- Baseline marker was explicit (`[H-T3-W01] baseline ...`) but this packet window is tracked as H-T3-W02 repeat.
- Baseline: Preset 4.
- Constraint behavior: left/right movement blocked; point allowed only slight down-angle adjustment.

### Packet H-T3-W02-A (baseline primary)
```text
15 00 4f 03 45 f7 ba 0b 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e3 02 df 03 01 00
00 00 00 00 00 00 3f 12 54 06 ca 12 3b 08 57 13
69 09 7a 13
```

### Packet H-T3-W02-B (post-action companion)
```text
15 00 52 03 6f 88 56 56 04 00 00 00 98 0e e0 13
d6 13 64 14 6b 14 bd 1c 00 00 00 1d e5 17 83 25
98 1a 05 26 76 1c 9d 26 07 1e 10 27 10 27 ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 98 3a 64 00 00 00 e8 03
0a 00 14 5a
```

### Packet H-T3-W02-C (post-action companion)
```text
15 00 55 03 50 3e 56 ff 04 00 00 00 98 0e e0 13
d6 13 64 14 6b 14 9f 1c 00 00 00 1d e5 17 83 25
98 1a 05 26 76 1c 9d 26 07 1e 10 27 10 27 ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 98 3a 64 00 00 00 e8 03
0a 00 14 5a
```

### Delta Interpretation
- Baseline primary remained Preset 4 signature with fixed sensitivity bytes (`0x4A/0x4C = 0x02E3/0x03DF`).
- Two consecutive subtype-`0x04` companion packets captured the constrained movement state.
- Local companion tuple changed from `... 6b 14 bd 1c 00 00 00 1d ...` to `... 6b 14 9f 1c 00 00 00 1d ...`, consistent with a small same-region adjustment rather than schema change.
- This repeat strengthens Tool3 region stability under boundary constraints and raises confidence from single mixed-action evidence to repeated behavior.

## HIP Tool4 Capture (H-T4-W01, Crash-Reconnect Then Downward Clean Move)

User-provided flow:
- Baseline marker used: `[H-T4-W01] baseline preset4 selected, Tool4 remove-handle mode, about to press Save`.
- Immediate crash/disconnect occurred, followed by reconnect and resumed capture.
- Post-reconnect action: downward move (no wall hit), chosen for cleaner path.

### Crash/Transport Context
- Session interruption observed (`Communication lost`, `Aborted Session`, repeated runtime originate errors `40080201`).
- Reconnect completed (`Transport Connected`, `Start Session`, `Navigating to: qrc:/Edit.qml`) before the useful packet sequence.

### Packet H-T4-W01-A (post-reconnect reference companion)
```text
15 00 77 03 a5 20 77 f2 04 00 00 00 98 0e e0 13
d6 13 64 14 6b 14 fa 14 99 15 00 1d e5 17 83 25
98 1a 05 26 76 1c 9d 26 07 1e 10 27 10 27 ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 98 3a 64 00 00 00 e8 03
0a 00 14 5a
```

### Packet H-T4-W01-B (post-action companion)
```text
15 00 7a 03 30 6e 77 a8 04 00 00 00 98 0e e0 13
d6 13 64 14 6b 14 f3 15 00 00 f9 1d 00 00 f9 25
91 02 05 26 76 1c 9d 26 07 1e 10 27 10 27 ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 98 3a 64 00 00 00 e8 03
0a 00 14 5a
```

### Packet H-T4-W01-C (post-action companion)
```text
15 00 7d 03 84 c5 83 f1 04 00 00 00 98 0e e0 13
d6 13 64 14 6b 14 d5 15 00 00 db 1d 00 00 db 25
90 02 05 26 76 1c 9d 26 07 1e 10 27 10 27 ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 98 3a 64 00 00 00 e8 03
0a 00 14 5a
```

### Delta Interpretation
- Despite crash noise, post-reconnect packets form a coherent subtype-`0x04` sequence in the known Tool4 companion region.
- Local rewrite neighborhood evolves from baseline-like values:
	- `... 6b 14 fa 14 99 15 00 1d e5 17 83 25 ...`
	- to `... 6b 14 f3 15 00 00 f9 1d 00 00 f9 25 91 02 ...`
	- to `... 6b 14 d5 15 00 00 db 1d 00 00 db 25 90 02 ...`
- Pattern matches prior Tool4 behavior signatures: late-region progressive rewrite with paired zeroing while packet family/layout remains stable.
- Confidence: medium-high for Tool4 regional mapping (crash-contaminated window, but coherent post-reconnect tuple progression).

## HIP Tool2 Capture (H-T2-W01, Square Edit With Rightward Wall Constraint)

User-provided flow:
- Baseline marker used: `[H-T2-W01] baseline preset4 selected, Tool2 square mode, about to press Save`.
- Action path: square edit, repeatedly constrained by wall; continued rightward attempts produced small progress.

### Packet H-T2-W01-A (baseline primary)
```text
15 00 b8 03 56 19 d8 8f 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e3 02 df 03 01 00
00 00 00 00 00 00 3f 12 54 06 ca 12 3b 08 57 13
69 09 7a 13
```

### Packet H-T2-W01-B (reference companion)
```text
15 00 b9 03 50 03 5a 41 04 00 00 00 98 0e e0 13
d6 13 64 14 6b 14 fa 14 99 15 00 1d e5 17 83 25
98 1a 05 26 76 1c 9d 26 07 1e 10 27 10 27 ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 98 3a 64 00 00 00 e8 03
0a 00 14 5a
```

### Packet H-T2-W01-C (post-action companion)
```text
15 00 bc 03 44 42 32 0b 04 00 00 00 98 0e e0 13
d6 13 64 14 6b 14 00 1d 96 15 00 1d e5 17 83 25
98 1a 05 26 76 1c 9d 26 07 1e 10 27 10 27 ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 98 3a 64 00 00 00 e8 03
0a 00 14 5a
```

### Delta Interpretation
- Baseline primary preserved Preset 4 signature and fixed sensitivity bytes (`0x4A/0x4C = 0x02E3/0x03DF`).
- Companion tuple neighborhood changed locally from:
	- `... 6b 14 fa 14 99 15 00 1d ...`
	- to
	- `... 6b 14 00 1d 96 15 00 1d ...`
- Rewrite is consistent with Tool2 square-shaping behavior already seen in ADS: selected local pair is re-quantized while the broader packet family/layout remains stable.
- Despite wall constraints, this is sufficient as representative Hip Tool2 evidence.

## HIP Tool1 Final Verification Attempt (H-T1-W03, Left Progression With Right Block)

User-provided flow:
- Intended sequence: baseline -> left -> right in one run.
- Observed behavior: rightward move at selected point was blocked; leftward movement succeeded and progressed.
- This window is treated as H-T1-W03 partial (left verified, right not achieved at this point).

### Packet H-T1-W03-A (reference companion)
```text
15 00 bf 03 cd 53 b6 c2 04 00 00 00 98 0e e0 13
d6 13 64 14 6b 14 fa 14 99 15 00 1d e5 17 83 25
98 1a 05 26 76 1c 9d 26 07 1e 10 27 10 27 ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 98 3a 64 00 00 00 e8 03
0a 00 14 5a
```

### Packet H-T1-W03-B (left progression primary)
```text
15 00 c2 03 ce a1 b9 c3 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e3 02 df 03 01 00
00 00 00 00 00 00 7a 13 84 06 7a 13 6b 08 7a 13
99 09 7a 13
```

### Packet H-T1-W03-C (left progression primary)
```text
15 00 c5 03 04 59 04 53 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e3 02 df 03 01 00
00 00 00 00 00 00 5c 13 83 06 5c 13 6a 08 7a 13
98 09 7a 13
```

### Packet H-T1-W03-D (left progression primary)
```text
15 00 c8 03 0c 80 ff 1b 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e3 02 df 03 01 00
00 00 00 00 00 00 00 00 8a 05 00 00 71 07 00 00
9f 08 7a 13
```

### Packet H-T1-W03-E (left progression primary)
```text
15 00 cb 03 d0 d5 cd 16 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e3 02 df 03 01 00
00 00 00 00 00 00 00 00 86 05 00 00 6d 07 00 00
9b 08 7a 13
```

### Delta Interpretation
- Sensitivity bytes remain fixed (`0x4A/0x4C = 0x02E3/0x03DF`).
- Companion region is stable; semantic movement appears in primary late tuple region.
- Leftward progression is visible as local x-anchor collapse and step-down:
	- `7a13 -> 5c13 -> 0000` in selected tuple x positions.
- Paired y values step down gradually (`8a05 -> 8605`, `7107 -> 6d07`, `9f08 -> 9b08`), consistent with constrained diagonal/down-left movement.
- Rightward motion was blocked at this chosen point, supporting a geometry/constraint-limited editor model rather than packet-schema change.

## HIP Tool1 Clean Right-Permissive Confirmation (H-T1-W04)

User-provided flow:
- Marker: `CLEAN RIGHT-PERMISSIVE TOOL1 CONFIRMATION`.
- Baseline from Preset 4, then right-permissive move at a point that allowed horizontal progress.

### Packet H-T1-W04-A (baseline primary)
```text
15 00 ce 03 b3 1f df aa 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e3 02 df 03 01 00
00 00 00 00 00 00 3f 12 54 06 ca 12 3b 08 57 13
69 09 7a 13
```

### Packet H-T1-W04-B (post-action companion)
```text
15 00 d1 03 92 80 4b 25 04 00 00 00 98 0e e0 13
d6 13 64 14 6b 14 00 1d e2 12 00 1d e5 17 83 25
98 1a 05 26 76 1c 9d 26 07 1e 10 27 10 27 ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 98 3a 64 00 00 00 e8 03
0a 00 14 5a
```

### Delta Interpretation
- Baseline matches known Preset 4 primary signature with fixed sensitivity bytes (`0x4A/0x4C = 0x02E3/0x03DF`).
- Post-action companion updates the same established late tuple neighborhood:
	- `... 6b 14 fa 14 99 15 00 1d ...`
	- to
	- `... 6b 14 00 1d e2 12 00 1d ...`
- This confirms right-permissive Tool1 movement is representable in the same schema/region family and resolves the previous right-block uncertainty as point-local geometry constraint rather than protocol limitation.

## HIP Tool4 Canonical Polish (Crash-Free, Includes Explicit Point Deletion)

User-provided flow:
- Marker: `Crash-free rerun of Tool4 for canonical polish`.
- First action deleted a point.
- Then selected another point, attempted right (blocked), then moved left.

### Packet H-T4-W02-A (reference companion)
```text
15 00 d4 03 6c e6 31 aa 04 00 00 00 98 0e e0 13
d6 13 64 14 6b 14 fa 14 99 15 00 1d e5 17 83 25
98 1a 05 26 76 1c 9d 26 07 1e 10 27 10 27 ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 98 3a 64 00 00 00 e8 03
0a 00 14 5a
```

### Packet H-T4-W02-B (deletion transition primary)
```text
15 00 d7 03 2a 8a 12 6b 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e3 02 df 03 01 00
00 00 00 00 00 00 3f 12 54 06 7a 13 98 0e e0 13
d6 13 64 14
```

### Packet H-T4-W02-C (deletion companion)
```text
15 00 d8 03 be 68 a4 69 04 00 00 00 6b 14 fa 14
99 15 00 1d e5 17 83 25 98 1a 05 26 76 1c 9d 26
07 1e 10 27 10 27 ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 98 3a 64 00 00 00 e8 03
0a 00 14 5a
```

### Packet H-T4-W02-D (post-delete move primary)
```text
15 00 db 03 e8 fc c8 e1 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e3 02 df 03 01 00
00 00 00 00 00 00 46 14 cb 04 46 14 0f 0d 64 14
4f 12 64 14
```

### Packet H-T4-W02-E (post-delete constrained-left primary)
```text
15 00 de 03 52 bc ab 79 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e3 02 df 03 01 00
00 00 00 00 00 00 00 00 4b 06 00 00 8f 0e 11 10
cf 13 64 14
```

### Delta Interpretation
- Crash-free sequence confirms Tool4 behavior without reconnect contamination.
- H-T4-W02-B/H-T4-W02-C capture explicit point-deletion transition (topology/tuple packing changes, not just value tweak).
- Subsequent primaries (D/E) show continued local tuple rewrites in the known late region after deletion, including constrained-direction adjustment when rightward motion is blocked.
- Sensitivity bytes remain fixed (`0x4A/0x4C = 0x02E3/0x03DF`) throughout, reinforcing separation between curve-topology edits and sensitivity controls.

## HIP Tool4 Delete-Only Confirmation (H-T4-W03, No Post-Delete Movement)

User-provided flow:
- Started from Preset 4 baseline.
- Deleted one point.
- Attempted to delete more than one point but could not.
- No post-delete drag/movement action in this window.

### Packet H-T4-W03-A (baseline primary)
```text
15 00 e1 03 2d f0 6f eb 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e3 02 df 03 01 00
00 00 00 00 00 00 3f 12 54 06 ca 12 3b 08 57 13
69 09 7a 13
```

### Packet H-T4-W03-B (baseline companion)
```text
15 00 e2 03 9f 27 99 ed 04 00 00 00 98 0e e0 13
d6 13 64 14 6b 14 fa 14 99 15 00 1d e5 17 83 25
98 1a 05 26 76 1c 9d 26 07 1e 10 27 10 27 ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 98 3a 64 00 00 00 e8 03
0a 00 14 5a
```

### Packet H-T4-W03-C (delete transition primary)
```text
15 00 e5 03 f0 d6 22 67 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e3 02 df 03 01 00
00 00 00 00 00 00 3f 12 54 06 7a 13 98 0e e0 13
d6 13 64 14
```

### Packet H-T4-W03-D (delete companion)
```text
15 00 e6 03 1f 93 3d b9 04 00 00 00 6b 14 fa 14
99 15 00 1d e5 17 83 25 98 1a 05 26 76 1c 9d 26
07 1e 10 27 10 27 ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 98 3a 64 00 00 00 e8 03
0a 00 14 5a
```

### Delta Interpretation
- Reproduces the same deletion transition pattern seen in H-T4-W02 without movement confounders:
	- primary late tuple rewrites from `... 3f 12 54 06 ca 12 3b 08 57 13 69 09 7a 13`
	- to `... 3f 12 54 06 7a 13 98 0e e0 13 d6 13 64 14`
- Companion also transitions from baseline-style head (`98 0e e0 13 ...`) to delete-followup layout (`6b 14 fa 14 ...`).
- Sensitivity bytes remain fixed (`0x4A/0x4C = 0x02E3/0x03DF`).
- Attempted multi-delete failing in the same window suggests UI-level constraint/state gating for additional removals, not missing packet capture.

## ADS Preliminary Capture (Single Sample)

### Packet ADS-A
```text
15 00 a9 00 8d fb 7b 50 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 9a 01 9a 01 01 00 00 00 00 00 00 00
06 0d 00 00 10 27 10 27 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff
```

### ADS Preliminary Notes
- Captured with same working filter (`type=0x15`, `subtype=0x00`, `len=0x64`).
- Single-sample candidate value pair appears at 0x34 and 0x36 (`0x019A`, mirrored).
- Byte 0x38 observed as `0x01` in this sample; semantic meaning unknown pending comparative capture.
- Requires at least one additional ADS save delta (N+1 or N-1) to confirm monotonic movement.

### Packet ADS-B
```text
15 00 af 00 93 8b 35 25 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 a4 01 a4 01 01 00 00 00 00 00 00 00
06 0d 00 00 10 27 10 27 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff
```

### Packet ADS-C
```text
15 00 b2 00 54 18 17 9e 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 9a 01 9a 01 01 00 00 00 00 00 00 00
06 0d 00 00 10 27 10 27 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff
```

### ADS Diff (B -> C)
- 0x02: 0xAF -> 0xB2
- 0x04: 0x93 -> 0x54
- 0x05: 0x8B -> 0x18
- 0x06: 0x35 -> 0x17
- 0x07: 0x25 -> 0x9E
- 0x34: 0xA4 -> 0x9A
- 0x36: 0xA4 -> 0x9A

### ADS Interpretation Update
- ADS candidate offsets are reinforced at 0x34 and 0x36 (mirrored values).
- Observed one-step delta is `0x000A` (0x01A4 <-> 0x019A), suggesting fixed-point scaling by 10 per UI step.
- 0x38 remained `0x01` across ADS captures and may be a mode/context flag rather than sensitivity value.

## ADS + Behavior Toggle Capture Set (Confirmed)

### Packet ADS-D (+1 step)
```text
15 00 c0 00 1b a3 2a 06 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 a4 01 a4 01 01 00 00 00 00 00 00 00
06 0d 00 00 10 27 10 27 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff
```

### Packet ADS-E (-1 step)
```text
15 00 c3 00 f6 28 c6 5c 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 9a 01 9a 01 01 00 00 00 00 00 00 00
06 0d 00 00 10 27 10 27 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff
```

### Packet ADS-F (switch custom -> native)
```text
15 00 c6 00 67 eb 4c 59 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 9a 01 9a 01 00 00 00 00 00 00 00 00
06 0d 00 00 10 27 10 27 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff
```

### Packet ADS-G (switch native -> custom)
```text
15 00 c9 00 10 df 83 03 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 9a 01 9a 01 01 00 00 00 00 00 00 00
06 0d 00 00 10 27 10 27 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff
```

### Confirmed ADS Findings From This Set
- Sensitivity value pair is confirmed at offsets 0x34/0x36.
- One UI step delta remains 0x000A (0x01A4 <-> 0x019A).
- Native/custom behavior flag is strongly indicated at offset 0x38:
	- custom: 0x01
	- native: 0x00
- 0x02 and 0x04-0x07 continue to drift as sequence/integrity fields.

## ADS Unlock Test (X/Y Independent Axis Confirmation)

### Packet ADS-X+1 (lock OFF, X increased, Y unchanged)
```text
15 00 cc 00 4c 6d 7e 21 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 a4 01 9a 01 01 00 00 00 00 00 00 00
06 0d 00 00 10 27 10 27 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff
```

### Packet ADS-Y+1 (lock OFF, Y increased, X unchanged)
```text
15 00 d3 00 3f 33 28 52 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 9a 01 a4 01 01 00 00 00 00 00 00 00
06 0d 00 00 10 27 10 27 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff
```

### ADS Unlock Interpretation
- X axis maps to offset 0x34 (0x019A <-> 0x01A4 with +/-1 step).
- Y axis maps to offset 0x36 (0x019A <-> 0x01A4 with +/-1 step).
- This confirms 0x34/0x36 are true independent ADS X/Y fields when lock is disabled.

## ADS Boundary Test (X -> 100)

### Packet ADS-BOUNDARY-HIGH-X
```text
15 00 3f 00 08 b1 30 6b 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 e8 03 a4 01 01 00 00 00 00 00 00 00
06 0d 00 00 10 27 10 27 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff
```

### ADS Boundary Interpretation Update
- ADS X (0x34/0x35) reached `0x03E8` when UI X was set to 100.0.
- ADS Y remained `0x01A4` (42.0), confirming axis independence at boundary.
- This confirms ADS X high clamp at 100.0 for current firmware path.

### Packet ADS-BOUNDARY-LOW-X (100 -> 0)
```text
15 00 42 00 80 dc 42 96 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 00 00 a4 01 01 00 00 00 00 00 00 00
06 0d 00 00 10 27 10 27 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff
```

### ADS Low Clamp Interpretation
- ADS X (0x34/0x35) reached `0x0000` when UI X was reduced from 100 to 0.
- ADS Y remained `0x01A4` (42.0), confirming axis independence at ADS low boundary.
- ADS X clamp is now confirmed as 0.0 -> 100.0 (0x0000 -> 0x03E8).

### Packet ADS-BOUNDARY-HIGH-Y (42 -> 100)
```text
15 00 48 00 a2 f6 db 5c 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 e8 03 01 00 00 00 00 00 00 00
06 0d 00 00 10 27 10 27 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff
```

### Packet ADS-BOUNDARY-LOW-Y (100 -> 0)
```text
15 00 4b 00 5f 2b 14 07 07 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
00 00 00 00 0a 00 00 00 01 00 00 00 00 00 00 00
06 0d 00 00 10 27 10 27 ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff
```

### ADS Y Boundary Interpretation
- ADS Y (0x36/0x37) reached `0x03E8` at UI Y = 100.0 and `0x0000` at UI Y = 0.0.
- ADS X remained `0x000A` (1.0) in both Y-boundary packets, confirming axis independence through Y sweeps.
- ADS clamps are now confirmed on both axes: 0.0 -> 100.0 (0x0000 -> 0x03E8).

## ADS Decimal Sweep (X: 1.0 -> 1.9)

### Captured Packet Values (offset 0x34/0x35)
- 1.1 -> `0x000B`
- 1.2 -> `0x000C`
- 1.3 -> `0x000D`
- 1.4 -> `0x000E`
- 1.5 -> `0x000F`
- 1.6 -> `0x0010`
- 1.7 -> `0x0011`
- 1.8 -> `0x0012`
- 1.9 -> `0x0013`

### Decimal Sweep Interpretation
- ADS X increments by exactly `+0x0001` per `+0.1` UI step.
- This is consistent with `stored = display * 10` and confirms tenths precision on ADS X in the low range.
- ADS Y remained `0x0000` in this sweep, so this set isolates X-axis decimal behavior cleanly.

### Runtime Note
- The first-chance `80000003` break shown after the sweep is a normal debugger break event and not a mapping anomaly.

## ADS Decimal Sweep (Y: 0.0 -> 0.9)

### Captured Packet Values (offset 0x36/0x37)
- 0.1 -> `0x0001`
- 0.2 -> `0x0002`
- 0.3 -> `0x0003`
- 0.4 -> `0x0004`
- 0.5 -> `0x0005`
- 0.6 -> `0x0006`
- 0.7 -> `0x0007`
- 0.8 -> `0x0008`
- 0.9 -> `0x0009`

### Decimal Sweep Interpretation (ADS Y)
- ADS Y increments by exactly `+0x0001` per `+0.1` UI step.
- ADS X remained `0x000A` (1.0), confirming axis isolation during the Y sweep.
- Combined with ADS X decimal captures, this confirms tenths precision on both ADS axes.
- Combined with boundary captures, ADS sensitivity mapping is now complete for current firmware path:
	- Axis offsets: X `0x34/0x35`, Y `0x36/0x37`
	- Scale: `stored = display * 10` (uint16 little-endian)
	- Clamp: `0.0 -> 100.0` (`0x0000 -> 0x03E8`)

### Runtime Note
- The first-chance `80000003` break shown after this sweep is an expected debugger event.

## HIP Decimal Sweep (Y: 100.0 -> 99.1)

### Captured Packet Values (offset 0x4C/0x4D)
- 99.9 -> `0x03E7`
- 99.8 -> `0x03E6`
- 99.7 -> `0x03E5`
- 99.6 -> `0x03E4`
- 99.5 -> `0x03E3`
- 99.4 -> `0x03E2`
- 99.2 -> `0x03E0`
- 99.1 -> `0x03DF`

### Decimal Sweep Interpretation (HIP Y)
- HIP Y changes by exactly `0x0001` per `0.1` UI step in the decreasing direction.
- HIP X remained `0x02E3` (73.9), confirming axis isolation during the Y sweep.
- Combined with HIP X decimal sweep (73.0 -> 73.9), this confirms tenths precision on both Hip axes.
- Combined with boundary captures, Hip sensitivity mapping is complete for current firmware path:
	- Axis offsets: X `0x4A/0x4B`, Y `0x4C/0x4D`
	- Scale: `stored = display * 10` (uint16 little-endian)
	- Clamp: `0.0 -> 100.0` (`0x0000 -> 0x03E8`)

## HIP Decimal Sweep (X: 73.0 -> 73.9)

### Captured Packet Values (offset 0x4A/0x4B)
- 73.1 -> `0x02DB`
- 73.2 -> `0x02DC`
- 73.3 -> `0x02DD`
- 73.4 -> `0x02DE`
- 73.5 -> `0x02DF`
- 73.6 -> `0x02E0`
- 73.7 -> `0x02E1`
- 73.8 -> `0x02E2`
- 73.9 -> `0x02E3`

### Decimal Sweep Interpretation (HIP X)
- HIP X increments by exactly `+0x0001` per `+0.1` UI step.
- HIP Y remained `0x03E8` (100.0), confirming axis isolation during the X sweep.
- This matches the fixed-point model `stored = display * 10` and confirms tenths precision for Hip X.

### Runtime Note
- The first-chance `80000003` break shown after this sweep is an expected debugger event.

## HIP Unlock Test (X/Y Independent Axis Confirmation)

### Packet HIP-X test (lock OFF, X changed, Y held)
```text
15 00 d7 00 26 71 04 db 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e4 02 da 02 01 00
00 00 00 00 00 00 06 0d 00 00 10 27 10 27 ff ff
ff ff ff ff
```

### Packet HIP baseline/intermediate
```text
15 00 db 00 99 cd dd 48 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 da 02 da 02 01 00
00 00 00 00 00 00 06 0d 00 00 10 27 10 27 ff ff
ff ff ff ff
```

### Packet HIP-Y test (lock OFF, Y changed, X held)
```text
15 00 de 00 c3 d9 f2 84 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 da 02 e4 02 01 00
00 00 00 00 00 00 06 0d 00 00 10 27 10 27 ff ff
ff ff ff ff
```

### HIP Unlock Interpretation
- Hip X maps to offset 0x4A.
- Hip Y maps to offset 0x4C.
- Independent movement is confirmed with lock disabled:
	- X-only state observed: 0x4A=0xE4, 0x4C=0xDA
	- Y-only state observed: 0x4A=0xDA, 0x4C=0xE4
- Mirrored state remains when lock is enabled (both bytes equal).

## Fixed-Point Scale Model (Confirmed)

- Hip and ADS both use the same encoding model:
	- stored_value = round(display_value * 10)
	- little-endian uint16 at axis offsets
- Verified examples:
	- 73.0 -> 730 -> 0x02DA
	- 74.0 -> 740 -> 0x02E4
	- 75.0 -> 750 -> 0x02EE
	- 76.0 -> 760 -> 0x02F8
	- 77.0 -> 770 -> 0x0302
	- 78.0 -> 780 -> 0x030C
- ADS captures follow same step granularity:
	- 41.0 -> 410 -> 0x019A
	- 42.0 -> 420 -> 0x01A4

This confirms +1.0 UI point corresponds to +0x000A in packet value.

## Boundary Test (Low Clamp)

### Packet HIP-BOUNDARY-LOW (X reduced from 73 to 0, Y unchanged)
```text
15 00 20 00 85 9c 36 d4 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 00 00 0c 03 00 00
00 00 00 00 00 00 06 0d 00 00 10 27 10 27 ff ff
ff ff ff ff
```

### Low Clamp Interpretation
- Hip X (0x4A/0x4B) reached `0x0000` when UI X was set to 0.
- Hip Y (0x4C/0x4D) remained `0x030C` (78.0), confirming independent axis persistence.
- This strongly indicates lower clamp for Hip X is 0.0 (stored as 0x0000).

## Boundary Sweep (Hip X: 0 -> 100)

### Packet HIP-BOUNDARY-1
```text
15 00 26 00 cb aa b9 17 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 0a 00 0c 03 00 00
00 00 00 00 00 00 06 0d 00 00 10 27 10 27 ff ff
ff ff ff ff
```

### Packet HIP-BOUNDARY-2
```text
15 00 29 00 bb b8 2d fa 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 a0 00 0c 03 00 00
00 00 00 00 00 00 06 0d 00 00 10 27 10 27 ff ff
ff ff ff ff
```

### Packet HIP-BOUNDARY-3
```text
15 00 2c 00 a9 48 c0 10 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 a8 02 0c 03 00 00
00 00 00 00 00 00 06 0d 00 00 10 27 10 27 ff ff
ff ff ff ff
```

### Packet HIP-BOUNDARY-4
```text
15 00 2f 00 ea 14 df dd 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 e8 03 0c 03 00 00
00 00 00 00 00 00 06 0d 00 00 10 27 10 27 ff ff
ff ff ff ff
```

### Boundary Interpretation Update
- Hip X at 0x4A/0x4B follows fixed-point value = display*10:
	- 0x000A -> 1.0
	- 0x00A0 -> 16.0
	- 0x02A8 -> 68.0
	- 0x03E8 -> 100.0
- Hip Y at 0x4C/0x4D remained 0x030C (78.0) across sweep.
- Combined with prior low-boundary capture (0x0000), Hip X clamp is now strongly indicated as 0.0 to 100.0.

## Boundary Test (Hip Y -> 0 with X held)

### Packet HIP-Y-BOUNDARY-1 (intermediate)
```text
15 00 32 00 28 6d 3f 1b 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 b2 02 0c 03 00 00
00 00 00 00 00 00 06 0d 00 00 10 27 10 27 ff ff
ff ff ff ff
```

### Packet HIP-Y-BOUNDARY-2 (intermediate)
```text
15 00 35 00 41 a1 cf e2 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 da 02 0c 03 00 00
00 00 00 00 00 00 06 0d 00 00 10 27 10 27 ff ff
ff ff ff ff
```

### Packet HIP-Y-BOUNDARY-3 (final Y=0)
```text
15 00 38 00 3c fb b2 97 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 da 02 00 00 00 00
00 00 00 00 00 00 06 0d 00 00 10 27 10 27 ff ff
ff ff ff ff
```

### Hip Y Clamp Interpretation
- Final capture confirms Hip Y (0x4C/0x4D) reaches `0x0000` when Y is set to 0.
- Hip X remained stable at `0x02DA` (73.0) in the final capture, confirming axis independence while reaching Y low clamp.

## Boundary Test (Hip Y -> 100)

### Packet HIP-Y-BOUNDARY-HIGH
```text
15 00 3b 00 74 a4 a7 0a 03 00 00 00 ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00
00 00 00 00 00 00 00 00 00 00 da 02 e8 03 00 00
00 00 00 00 00 00 06 0d 00 00 10 27 10 27 ff ff
ff ff ff ff
```

### Hip Y High Clamp Interpretation
- Hip Y (0x4C/0x4D) reached `0x03E8` when UI Y was set to 100.0.
- Hip X remained stable at `0x02DA` (73.0).
- Combined with prior Y low capture (`0x0000`), Hip Y clamp is confirmed as 0.0 -> 100.0.

## ADS Activation/Deactivation Delay Variant (Preliminary, Main HUD -> Edit Path)

User-provided flow:
- Start from main HUD screen.
- Navigate to Edit, then ADS sensitivity activation section.
- Change Activate delay by +1 then back to 0.
- Change Deactivate delay by +2 then back to 0.

### Packet ADS-DELAY-A (metadata/name container)
```text
15 00 f5 03 82 95 e9 01 00 00 00 00 45 74 68 61
6c 20 69 73 20 43 68 65 61 74 69 6e 67 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 d7 10 0e 04
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 01 00 e8 03
02 00 01 00
```

### Packet ADS-DELAY-B (metadata/name container variant)
```text
15 00 f8 03 62 65 61 a0 00 00 00 00 45 74 68 61
6c 20 69 73 20 43 68 65 61 74 69 6e 67 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 d7 10 0e 04
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 01 00 e8 03
02 00 00 00
```

### Packet ADS-DELAY-C (control variant, candidate nonzero)
```text
15 00 fb 03 e7 4d d3 48 01 00 00 00 02 00 00 00
01 00 08 00 01 01 10 0e 64 00 1e 00 00 00 00 00
14 5a 08 02 04 00 00 00 00 00 62 00 87 13 c4 00
0e 27 ea 13 0f 27 10 27 10 27 ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff
```

### Packet ADS-DELAY-D (control variant, candidate reset)
```text
15 00 fe 03 26 26 fb c8 01 00 00 00 00 00 00 00
01 00 08 00 01 01 10 0e 64 00 1e 00 00 00 00 00
14 5a 08 02 04 00 00 00 00 00 62 00 87 13 c4 00
0e 27 ea 13 0f 27 10 27 10 27 ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff
```

### Preliminary Interpretation
- This run surfaced a different packet family from the curve-edit captures (includes metadata/name container packets and a control variant).
- In control-variant packets (`... 48 01 ...` / `... c8 01 ...`), a candidate delay field changed from `0x00000002` to `0x00000000` at offset `0x0C`.
- This is consistent with a "set delay to nonzero then reset to zero" pattern, but exact semantic split between Activate and Deactivate is still provisional.
- Next confirming run should isolate one variable at a time (min->max->min for Activate only, then Deactivate only), with explicit `.echo` start/target/actual tags.

### Confirmation Update (Main HUD -> Edit, Chunked Sweep)
- Activate sweep to 1000ms confirmed in metadata/name packet family tail:
	- `... 01 00 e8 03 02 00 XX XX`
	- `XX XX` progressed through sampled values up to `0x03E8` (1000).
- Deactivate sweep to 500ms confirmed in control family with mutable field at `0x0C..0x0F`:
	- observed values: `0x00000001`, `0x0000002E`, `0x0000007B`, `0x000000EE`, `0x000001F4`.
- Working split (provisional -> strong):
	- Activate delay: metadata family, `uint16` at `0x62/0x63`.
	- Deactivate delay: control family, `uint32` at `0x0C..0x0F`.
- Chunked stepping strategy is sufficient because field progression is monotonic and endpoints were observed.

### Confirmation Update 2 (ADS Page, Return-To-Zero + 0->3->0 Micro-Ramp)
- Baseline reset run produced expected zero-state packets in both families:
	- Metadata/name tail observed at `... 01 00 e8 03 02 00 00 00`.
	- Control family mutable field observed at `0x0C..0x0F = 0x00000000`.
- Subsequent 3-click ramp and reset showed clean monotonic transitions in one family:
	- Control family `0x0C..0x0F`: `0x00000001 -> 0x00000002 -> 0x00000003 -> 0x00000002 -> 0x00000001 -> 0x00000000`.
- Metadata/name family in same capture window showed tail ramp samples:
	- `... 02 00 01 00 -> 02 00 02 00 -> 02 00 03 00 -> 02 00 02 00 -> 02 00 01 00 -> 02 00 00 00`.
- Marker caveat:
	- One intended marker command was entered as `.first ...` (syntax error), so this window should be treated as semantically strong but label-order ambiguous.
	- Field identity is still preserved by packet-family structure and monotonic value behavior.
- Decision:
	- Evidence is sufficient to proceed with sender implementation using the current split.
	- Optional audit-only rerun can be done later with explicit `.echo` tags per click if label-pure provenance is required.

### Confirmation Update 3 (ADS Page, Explicit Isolated 0->2->0 Runs)
- Marker-tagged isolated Activate run:
	- Marker: `starting activate from 0, upping by 2, returning to 0`.
	- Metadata/name tail progression observed exactly:
		- `... 01 00 e8 03 02 00 01 00`
		- `... 01 00 e8 03 02 00 02 00`
		- `... 01 00 e8 03 02 00 01 00`
		- `... 01 00 e8 03 02 00 00 00`
	- Confirms Activate delay field as `uint16` at metadata tail (`0x62/0x63`) in a label-pure window.
- Marker-tagged isolated Deactivate run:
	- Marker: `deactive start 0, upping by 2, returning to zero`.
	- Control-family field progression at `0x0C..0x0F`:
		- `0x00000001`
		- `0x00000002`
		- `0x00000001`
		- `0x00000000`
	- Confirms Deactivate delay as `uint32` at control-family `0x0C..0x0F` in a label-pure window.
- Closure:
	- Prior `.first` marker typo caveat is now fully retired by these explicit isolated captures.
	- ADS delay split is closed for current firmware path.

## Smart Actions Remap Capture (RT Baseline Remap Test)

User-provided flow:
- Remapped RT to the Xbox button.
- Kept RT as the baseline control.
- Expanded the UI window to inspect the configuration fields.
- Did not delete the smart action after capture.

Observed packet shape:
- Type `0x15` packet family with repeated selector-like bytes around `0x4F` and `0x52`.
- The visible pressure/threshold fields changed across the window as the trigger configuration was edited.

Representative samples:
```text
15 00 aa 04 6b 9d f7 60-15 00 00 00 01 00 4f 17
ba c0 ff 06 01 00 52 17-00 c0 ff 00 00 00 00 00

15 00 ad 04 4b 48 ec 45-15 00 00 00 01 00 4f 17
ba c0 ff 06 01 00 52 17-a4 c0 ff 02 64 00 00 00

15 00 98 04 cb ea f8 ff-15 00 00 00 01 00 4f 17
ba c0 ff 06 01 00 52 17-a4 c0 ff 02 36 00 00 00

15 00 9b 04 d8 d2 38 54-15 00 00 00 01 00 4f 17
ba c0 ff 06 01 00 52 17-a4 c0 ff 02 01 00 00 00
```

Preliminary interpretation:
- This looks more like a shared Smart Actions trigger template with selector bytes plus parameter fields than a separate offset per destination button.
- The remap target itself may be encoded as a button selector inside the same payload rather than as a dedicated button-specific address.
- Best next comparison: repeat the same RT baseline with a different target button and diff only the selector/parameter cluster.

Follow-on capture note:
- After removing the Xbox button target, the same Smart Action window was repurposed to the joystick angle/magnitude control.
- The new state kept the same trigger family shape, but the edited fields now reflect control-mode configuration rather than button destination selection.
- The typed WinDbg command had a leading-text typo on one line, but the packet evidence itself is intact.
- Practical read: the payload appears to have a shared remap/control schema where destination buttons and joystick behavior modes occupy related fields, not separate per-button offsets.

Same-window comparison (Magnitude -> Aim Angle):
- User confirmed: same baseline, same open window; removed Magnitude and replaced with Aim Angle.
- Captured pair:
```text
15 00 b9 04 87 a7 67 fb-15 00 00 00 01 00 4f 17
ba c0 ff 06 01 00 52 17-a4 c0 ff 02 64 00 00 00

15 00 bc 04 18 08 4d 11-15 00 00 00 01 00 4f 17
ba c0 ff 06 01 00 52 17-a4 c0 ff 06 64 00 58 ca
```
- Stable bytes around trigger selectors remained intact (`... 4f 17 ... 52 17 ... a4 c0 ff ...`).
- Action/control mode byte changed from `0x02` to `0x06` at offset `0x1B`.
- A trailing two-byte parameter became nonzero (`0x0000 -> 0xCA58` at `0x1E/0x1F`).
- Interpretation:
	- This strongly indicates a mode discriminator plus mode-specific parameter payload (not destination-button-specific offsets).
	- Aim Angle appears to carry a numeric parameter where prior mode had none/zero in this slot.

Aim Angle parameter sweep (same window, RT baseline held):
- User action: started at 180 degrees, moved to max (359), then moved to 0.
- Captures:
```text
15 00 bf 04 0c 8b 9d 6f-15 00 00 00 01 00 4f 17
ba c0 ff 06 01 00 52 17-a4 c0 ff 06 64 00 5f d1

15 00 c2 04 ed 7d 42 ce-15 00 00 00 01 00 4f 17
ba c0 ff 06 01 00 52 17-a4 c0 ff 06 64 00 50 c3
```
- Observed mutable field remains `0x1E/0x1F` while mode byte `0x1B=0x06` stays fixed.
- Values seen so far for Aim Angle slot (`uint16`, little-endian):
	- `0xCA58` = 51800 (earlier capture around 180 deg)
	- `0xD15F` = 53599 (max-end sweep capture)
	- `0xC350` = 50000 (0-end sweep capture)
- Working encoding hypothesis (strong):
	- `encoded_angle = 50000 + angle_tenths`
	- Evidence fit:
		- 0.0 deg -> 50000 (`0xC350`)
		- 180.0 deg -> 51800 (`0xCA58`)
		- 359.9 deg -> 53599 (`0xD15F`) or near-max rounding if UI displays 359.

Validation run (high-sensitivity slider, max/90/0 sequence):
- User flow: attempted 0 -> max (359.9), then to 89 with single-click steps to 90, then return to 0.
- Captured Aim Angle values in `0x1E/0x1F` while mode stayed `0x06`:
	- `0xC6CA`, `0xC6CB`, `0xC6CF`, `0xC6D3`, `0xC6D4`
	- final return sample: `0xC350`
- Key confirmation point:
	- `0xC6D4` = 50900, which matches 90.0 deg under `50000 + angle_tenths`.
	- `0xC350` = 50000 confirms 0.0 deg base on return.
- Conclusion:
	- Aim Angle encoding is confirmed as `encoded_angle = 50000 + angle_tenths`.
	- Semantic units: Angle is circumferential position in degrees around a full circle (0.0 -> 359.9).
	- Slider sensitivity affects operator precision but not field semantics.

Magnitude follow-up run (with reconnect hiccup):
- User flow:
	- Switched Angle -> Magnitude and set to 0.
	- Observed note: Magnitude default appears to start at 10.
	- Swept values, then transport dropped and session reconnected.
	- After reconnect, continued in same logical window: 3600 -> 166 -> 165 -> ... -> 0.
- Key packets:
```text
15 00 da 04 ... a4 c0 ff 02 64 00 00 00
15 00 dd 04 ... a4 c0 ff 06 64 00 2c b0
15 00 e0 04 ... a4 c0 ff 06 64 00 c8 af
...
15 00 04 05 ... a4 c0 ff 06 64 00 44 b6
15 00 07 05 ... a4 c0 ff 06 64 00 3d b6
15 00 0a 05 ... a4 c0 ff 06 64 00 3c b6
15 00 13 05 ... a4 c0 ff 06 64 00 c8 af
```
- Interpreting `0x1E/0x1F` as uint16 little-endian:
	- `0xB02C` = 45100 (matches Magnitude 10.0)
	- `0xAFC8` = 45000 (matches Magnitude 0.0)
	- `0xB644` = 46660 (matches 166.0)
	- `0xB63D` = 46653 (near 165.x during click-step)
	- `0xB63C` = 46652 (near 165.x during click-step)
- Working Magnitude encoding (strong):
	- `encoded_magnitude = 45000 + magnitude_tenths`
	- Expected max 360.0 (or UI 3600 tenths) -> `48600` (`0xBDD8`); observed near-max sample `0xBDE1` is consistent with small slider overshoot/noise.
- Caveat:
	- Reconnect interrupted continuity, so this is marked strong but not fully closure-grade until one clean no-reconnect min/max/mid pass is captured.

Clean rerun (no reconnect) for Magnitude:
- User markers:
	- `clean rerun attempt of mag`
	- `started at 0, maxed to 3600/s`
	- `reducing to halfway mark`
	- `stopped at 185, continuing to 0`
- Captured values at `0x1E/0x1F` (uint16 LE), mode remained `0x06`:
	- `0xBDE1` = 48609 (max-end capture, near expected 360.0 endpoint)
	- `0xB702` = 46850 (exactly matches 185.0)
	- `0xAFC8` = 45000 (exactly matches 0.0)
- Confirmation math:
	- 185.0 -> `45000 + 1850 = 46850` -> `0xB702`
	- 0.0 -> `45000 + 0 = 45000` -> `0xAFC8`
	- max-end sample remains within expected high-end behavior for `45000 + magnitude_tenths`.
- Conclusion update:
	- Magnitude encoding is now confirmed as `encoded_magnitude = 45000 + magnitude_tenths`.
	- Semantic units: Magnitude is angular speed output (deg/s), with UI max reported as 3600 deg/s.
	- Remaining variance at max appears to be UI slider endpoint granularity, not a schema change.

## Smart Action: Config Switch (Adjacent Config) Capture

User flow:
- Kept same RT baseline and same Smart Actions edit window.
- Added Smart Action button for switching to adjacent config.
- Saved in editor and returned to HUD.
- Pressed RT on controller to trigger runtime config switch.

Captured during editor/save path:
```text
15 00 2e 05 ... 15 00 00 00 01 00 4f 17 ... a4 c0 ff 06 64 00 90 e2
15 00 31 05 ... 11 00 00 00 ...
15 00 32 05 ... 12 00 00 00 ...
15 00 33 05 ... 13 00 00 00 ...
15 00 34 05 ... 14 00 00 00 ...
15 00 35 05 ... 15 00 00 00 ...
```

Interpretation:
- This introduced a new variable-length payload family under subtype `0x05` with chunk-like lengths/count prefixes (`0x11..0x15`).
- The burst appears during Smart Action authoring/serialization (save/edit path), not during existing angle/magnitude scalar edits.

HUD runtime trigger result:
- User confirmed RT-triggered config switch occurred on HUD, but no `BOUNDARY_TEST` packet followed in this manager write hook.
- Most likely reason: controller-triggered switch executes device-side and does not require an app-originated BLE write, so it is not visible from this breakpoint location.
- Additional runtime path observed:
	- Enter navigation mode via controller combo (D-pad Left + B), then press Select to switch config from HUD.
	- User observed a brief "half-restart" side effect: authentication controller loses power briefly, then re-enumerates/vibrates again.
	- This behavior is consistent with a short transport/device reinitialization during config activation.

Actionable next step for runtime confirmation:
- Capture a manual app-driven config switch from HUD/UI controls (not controller trigger) to observe app-side write semantics for config activation.
- Also capture around navigation-mode switch boundaries (pre-combo, combo entry, Select switch, immediate post-switch) to correlate with reconnect/power-cycle telemetry.

Manual app-driven HUD switch test (CFG-UI-W01):
- Markers used:
	- `[CFG-UI-W01] HUD baseline before manual app switch`
	- `[CFG-UI-W01] manual app switch A->B just performed`
	- `[CFG-UI-W01] manual app switch B->A just performed`
- Observed output between markers:
	- UI navigation lines only (`Navigating to: qrc:/Load.qml`, `Navigating to: qrc:/HUD.qml`).
	- No `BOUNDARY_TEST` packets were emitted after either manual app switch.
- Closure for this path:
	- App-driven HUD config switching also produces no visible manager write burst at current hook location.
	- Combined with controller-triggered results, config activation is concluded to be device-side (or otherwise outside this write interception point) for this capture path.

Follow-up attempt (SA editor open + nav-mode switch):
- Marker: `added smart action to switch profiles, leaving window OPEN but switching to nav mode and then performing switch`.
- Result: switch does not execute while Smart Action editor is open (`wont perform switch with SA open`).
- After saving newly added switch action, subtype `0x05` burst emitted again with contiguous chunks:
	- `15 00 a8 05 ... 11 00 00 00 ...`
	- `15 00 a9 05 ... 12 00 00 00 ...`
	- `15 00 aa 05 ... 13 00 00 00 ...`
	- `15 00 ab 05 ... 14 00 00 00 ...`
	- `15 00 ac 05 ... 15 00 00 00 ...`
- Notable detail: chunk `a8 05` contains duplicated switch record tuple (`... a4 c0 ff 06 64 00 90 e2 ... a4 c0 ff 06 64 00 90 e2 ...`), consistent with list serialization including repeated entries.
- User conclusion from run: switch failed and RT baseline trigger needs adjustment before next runtime attempt.

Baseline-reset retry (new baseline + re-added switch SA):
- Marker: `choosing new baseline, and re adding new switch SA`.
- Authoring/save path produced another rich subtype `0x05` burst set, including both list-style chunks (`0x11..0x15`) and record-style chunks (`0x10`) with switch-related tuples.
- Representative sequence observed:
	- `15 00 c6 05 ... 10 00 00 00 ...`
	- `15 00 c7 05 ... 11 00 00 00 ...`
	- `15 00 c8 05 ... 12 00 00 00 ...`
	- `15 00 c9 05 ... 13 00 00 00 ...`
	- `15 00 ca 05 ... 14 00 00 00 ...`
	- `15 00 cb 05 ... 15 00 00 00 ...`
	- additional `0x10` chunks (`ce 05`, `d1 05`) persisted with nearby switch tuple permutations.
- Runtime outcome:
	- User reports switch still could not be performed.
	- Confirms that changing baseline alone did not unblock runtime switch execution in this scenario.

HUD-entry auto-switch observation:
- Marker: `adding SA, returning to HUD, performing switch`.
- On return to HUD after save, config switched automatically before explicit trigger input.
- User note: previously created switch action remained present (did not require re-adding), indicating persistent action state across attempts.
- Implication:
	- Runtime switch can fire as a state-transition side effect on HUD entry when a saved switch SA is already active.
	- Future runtime tests must control for pre-existing switch SA state and trigger mode to avoid false "manual trigger" attribution.

Control run (delete old switch SA, recreate from clean baseline):
- User flow:
	- Confirmed no old switch SA present on current switched profile.
	- Returned to baseline HUD, deleted old switch SA, created a new switch SA, saved, and exited to HUD.
- Save path again produced expected subtype `0x05` authoring burst (`ed..f2` then `f5..ff` with `0x10..0x15` chunks and selector tuples).
- Runtime outcome on HUD entry:
	- `no auto switch happened after creating new switch and leaving to main HUD`.
- Interpretation update:
	- Auto-switch-on-HUD-entry is conditional (likely stale/persistent prior switch-state interaction), not guaranteed behavior for every newly created switch SA.
