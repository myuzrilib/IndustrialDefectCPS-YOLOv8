# Operator dashboard

`dashboard.py` — a Streamlit panel that reads the event log and renders it live.

```bash
streamlit run dashboard.py
```

Start `../inference/final.py` first. The dashboard reads `tespiti_log.csv` and will say so
rather than render if the file does not exist yet.

It only ever **reads** the log. It holds no state of its own and never writes, so it can
be started, stopped or crashed at any point without affecting the sorting loop.

## What it shows

| | |
|---|---|
| Metrics | session total, defect count, defect percentage, most frequent class |
| Charts | class distribution, and detections per minute |
| Table | every event in the session, sortable |
| Alarm | fires when *n* defective components arrive **consecutively** |
| Export | CSV download, or one-click upload of the log to Google Sheets |

The consecutive-defect threshold is set in the sidebar, default five. Consecutive defects
are the signal that something upstream has gone wrong — a lighting change, a feed
problem, a bad batch — rather than that one part is bad.

Auto-refresh is five seconds and can be switched off. **Reset session** sets a new start
time and shows only events after it; the underlying log is not modified.

## Google Sheets export

Uses PyDrive2 and needs OAuth credentials. The first upload opens a browser for consent
and writes `credentials.json` beside the script; later uploads reuse and refresh it.

`credentials.json` is a secret — do not commit it.

## Dependencies

`streamlit`, `pandas`, `plotly`, `pydrive2`. `logo.png` in `../inference/` is shown in
the sidebar when present and is optional.
