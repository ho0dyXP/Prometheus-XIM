# Capture Archive

This folder stores durable packet-capture evidence independent of chat history.

## Structure

- `CAPTURE_TEMPLATE.md`: copy this for each new session
- `windbg_window_marker_cheatsheet.txt`: copy/paste WinDbg `.echo` marker flow for windowed captures (H-T2-W01/H-T3-W01/H-T4-W01)
- `YYYY-MM-DD_session-N.md`: completed session notes
- `raw/`: optional raw WinDbg `.logopen` outputs

## Workflow

1. Copy `CAPTURE_TEMPLATE.md` to a date-stamped session file.
2. Capture baseline and modified packet dumps.
3. Record diff and interpretation.
4. Keep raw WinDbg logs for auditability.

## Naming Convention

- Notes: `2026-04-13_session-1.md`
- Raw logs: `raw/2026-04-13_session-1_windbg.log`

## Promotion Rule

Only move findings into `reference/packet_reference.yaml` after at least two reproducible captures.
