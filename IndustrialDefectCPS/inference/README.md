# Host application

`final.py` — the sorting loop. Captures frames, segments each component, applies the
commanded delay, dispatches the serial identifier, and writes one row per event to
`tespiti_log.csv`.

Run it from this directory so the relative paths resolve:

```bash
python final.py
```

## Configuration, at the top of the file

| | |
|---|---|
| `MODEL_PATH` | `best.pt` — copy the checkpoint from `../train/best.pt/` beside this script |
| `SERIAL_PORT` | the port the ESP32 enumerated as (`COM9` as committed) |
| `CONVEYOR_SPEED` | **0.054 m/s** — measured on the belt, not nominal |
| `OFFSET_METERS` | 0.30 m, camera optical centre to the trigger point |
| `DISTANCES` | station distance per class, in metres |
| `SERVO_SIGNALS` | the byte sent to the ESP32 per class |
| `CLASS_TRANSLATION` | model class names to sorting labels |

Retargeting the cell to a different conveyor or a different number of stations is an edit
to `DISTANCES` and `SERVO_SIGNALS`, not a code change.

## Timing

The commanded delay is `(DISTANCES[class] - OFFSET_METERS) / CONVEYOR_SPEED`, measured
from the detection frame. The arm then holds for 5,000 ms, so the component is deflected
if it arrives anywhere inside that window.

**Measure `CONVEYOR_SPEED` on your own belt.** The delay scales directly with it: at the
2.00 m station a 15% error is about five seconds, which is the entire gate window.

## Class translation

The checkpoint labels its classes in Turkish; the sorting logic is written against English
labels. `CLASS_TRANSLATION` bridges them and raises `KeyError` on any unmapped class, so
a class that would never be sorted is reported rather than skipped.

`kusur` maps to `None`: it marks a defect region rather than a quality grade, so it is not
a sorting target.

> **Verify the five pairings against your own cell before running it.** They were derived
> from the class names. A wrong pairing sends a component to the wrong bin *without*
> raising an error, which is worse than no detection at all.

## Trigger

Components are detected by a glare trigger rather than continuously: `TRIGGER_BOX_WIDTH`,
`BRIGHTNESS_THRESHOLD`, `MIN_GLARE_AREA` and `COOLDOWN_TIME` define the region and the
reflection that starts an inference. Tune these to your illumination before tuning
anything else.

## Output

`tespiti_log.csv` — `Timestamp, Class, Cumulative_Count, Code, Sub_Class`, one row per
event. The copy committed here is an empty template; the log from the validation session
is on [Zenodo](https://doi.org/10.5281/zenodo.19928743), and every throughput and
success-rate figure in the paper is recomputable from it.

`frames/` — annotated inference outputs, written per detection. Create it before the
first run.
