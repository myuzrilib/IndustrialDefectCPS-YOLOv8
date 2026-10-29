# Bring-up procedure

How to configure, deploy and run the sorting cell. For what the system is and how it
works, see the [repository README](../README.md).

The system runs as two processes that share nothing but a file: `final.py` drives the
sorting loop and writes an event log; `dashboard.py` reads that log and renders it. The
dashboard can be started, stopped or crashed at any time without affecting sorting.

---

## Phase 1 — software

### 1. Environment

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install opencv-python ultralytics pyserial numpy tqdm \
            streamlit pandas plotly pydrive2
mkdir -p inference/frames
```

`frames/` holds the annotated inference outputs written during a session.

### 2. Model weights

`train/best.pt/best.pt` is the checkpoint every reported figure was measured with. Copy it
beside `inference/final.py`, or point `MODEL_PATH` at it.

> **Class names.** The checkpoint labels its classes in Turkish, while the sorting logic
> is written against English labels. `final.py` carries a `CLASS_TRANSLATION` table that
> bridges the two and raises `KeyError` on any unmapped class, so nothing fails silently.
> **Verify the five pairings against your own cell before running it** — a wrong pairing
> sends a component to the wrong bin without raising an error.

### 3. Firmware

Open `Edge PLC/plc_system/plc_system.ino` in the Arduino IDE or PlatformIO. Install the
**Adafruit PWM Servo Driver** library from the Library Manager (a copy is in
`Edge PLC/` if the manager is unavailable), then flash the ESP32 over USB.

On reset the firmware cycles all four arms as a self-test. Use that to confirm channel
order and mechanical clearance before putting anything on the belt.

---

## Phase 2 — hardware

### 1. Power

Bring up the conveyor, the laptop, the operator monitor, the camera and the servo supply
adapters, and confirm each is stable before connecting anything.

The servos run from a **dedicated supply rail**, not from the ESP32 regulator: four MG995
units under simultaneous stall exceed what the board can deliver. Tie the grounds
together.

### 2. Serial port

Find the port the ESP32 enumerated as — Device Manager on Windows, `ls /dev/tty*` on
Linux or macOS — and set `SERIAL_PORT` in `final.py` to match. It is `COM9` as committed.

### 3. Camera

The industrial camera connects through a USB–HDMI capture card. Laptops assign their
built-in webcam index 0, so the capture index in `cv2.VideoCapture()` is usually 1 or 2 —
check it before a run.

### 4. Geometry

`final.py` declares the physics at the top of the file:

```python
CONVEYOR_SPEED = 0.054     # m/s, measured on the belt
OFFSET_METERS  = 0.30      # camera optical centre to the trigger point
DISTANCES      = { ... }   # station distance per class, in metres
```

**Measure the belt velocity on your own conveyor.** Mark a point, time its travel over
1 m, repeat three times. Every commanded delay is `distance / CONVEYOR_SPEED`, so an error
here scales directly into mistimed deflections — at the far station, a 15% error is about
five seconds, which is the whole gate window.

Station distances are measured from the **camera optical centre**, not from the chamber
wall.

---

## Phase 3 — run

```bash
# terminal 1 — the sorting loop
cd inference && python final.py

# terminal 2 — the operator dashboard
cd dashboard && streamlit run dashboard.py
```

Start the sorting loop first: the dashboard reads `tespiti_log.csv`, and until that file
exists it will say so rather than render.

Let the belt reach steady speed before feeding the first component. Sorting success in
the opening minutes of a session is measurably lower than in steady state.

Keep components destined for the same station at least 5,000 ms apart — that is the
configured arm hold interval, and a second component arriving inside an open gate will
follow the first.

**Safety.** The arms actuate without local warning whenever a command arrives over
serial. Do not reach into the belt path while `final.py` is running. Stop it before
clearing a jam, and power down the servo rail before any mechanical adjustment.

---

## What the dashboard shows

Session totals, defect count and percentage, and the most frequent class; a
class-distribution bar chart and a per-minute detection trend; a sortable detail table;
CSV download and one-click upload of the session log to Google Sheets.

An operator-set threshold raises an on-screen alarm when that many defective components
arrive **consecutively** — the signal that something upstream has gone wrong, rather than
that one part is bad. Default is five.

The session can be reset from the sidebar, which sets a new start time and shows only
events after it. The underlying log is never modified.
