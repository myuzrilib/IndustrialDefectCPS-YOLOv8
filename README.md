# Industrial Defect CPS — a low-cost cyber-physical sorting cell

A conveyor-paced quality-inspection cell that segments each component with YOLOv8s-seg on
a passively cooled laptop CPU and deflects it into one of four bins with servo-driven
arms. Built for **US$1,548** from commodity parts.

Everything needed to rebuild it is in this repository. The dataset and the raw session
log are deposited on Zenodo.

| | |
|---|---|
| Perception | USB webcam in an enclosed chamber; YOLOv8s-seg, six trained classes |
| Inference host | Acer Swift 1, passively cooled, CPU only — **605 ms** mean acquisition to serial dispatch |
| Control | ESP32 over USB serial at 115,200 baud → PCA9685 16-channel PWM controller |
| Actuation | Four MG995 servos at 0.50, 1.00, 1.50 and 2.00 m from the camera |
| Belt speed | 0.054 m/s |
| Reporting | Streamlit dashboard reading the event log live |
| Accuracy | mAP@0.5 **93.8%**, mAP@0.5:0.95 **89.0%** |
| Sorting success | **91.44%** overall, **95.15%** in steady state, over 327 events |

## Layout

```
hardware/                      printed brackets, drawings, parametric CAD source
IndustrialDefectCPS/
├── Edge PLC/plc_system/       ESP32 firmware
├── inference/                 host application and the event log
├── dashboard/                 Streamlit operator dashboard
├── train/                     training script and the trained checkpoint
└── data/                      dataset configuration
```

Each directory has its own README with what the files do and how to run them.

## How it works

**Perception.** A webcam images each component inside an enclosed chamber under
controlled illumination. The host segments it and assigns a quality grade.

**Actuation.** Each deflection station is two 3D-printed PLA brackets and one hand-formed
PVC blade. The fixed bracket carries the servo and clamps to the conveyor frame through a
slot that sets the servo height. The moving arm is keyed to the rectangular servo horn by
a pocket in the underside of its plate, so arm, blade and horn turn as one rigid body.

**Gated deflection.** The host delays serial dispatch by a commanded interval measured
from the detection frame, and the arm then stays open for 5,000 ms. A component is
deflected if it arrives anywhere inside that window rather than at one precise instant, so
the cell absorbs seconds of cumulative timing error. This is what makes the design work on
commodity hardware, and it is the reason the limiting factor is the actuator rather than
the vision model.

**Reporting.** The host writes one row per event to a CSV log. The dashboard reads that
file every five seconds and shows live counts, defect rate, class distribution, a
per-minute trend, and an alarm when defects arrive consecutively.

## Quick start

```bash
python -m venv venv && source venv/bin/activate
pip install opencv-python ultralytics pyserial numpy tqdm streamlit pandas plotly pydrive2

# terminal 1 — the sorting loop
cd IndustrialDefectCPS/inference && python final.py

# terminal 2 — the operator dashboard
cd IndustrialDefectCPS/dashboard && streamlit run dashboard.py
```

Set `SERIAL_PORT` and the camera index in `final.py` first; see
`IndustrialDefectCPS/README.md` for the full bring-up procedure.

## Dataset

665 original images of proxy spherical defects, partitioned **333 / 173 / 159 before
augmentation**. The training split is augmented threefold, giving 999 / 173 / 159.
Annotations are COCO polygons.

Six trained classes — `cok iyi`, `yari iyi`, `iyi cig`, `curuk`, `kusur`, `cok kotu` —
of which five are quality grades and one (`kusur`) marks defect regions. The five grades
map to four physical stations, two of them sharing the station at 2.00 m.

Full dataset and the raw session log: [10.5281/zenodo.19928743](https://doi.org/10.5281/zenodo.19928743)

## Model

`IndustrialDefectCPS/train/best.pt/best.pt` — YOLOv8s-seg, 150 epochs, AdamW, 640 px.
This is the checkpoint `final.py` loads and the one every reported figure was measured
with. `train/yolov8s.py` exports an ONNX copy as its final step, so an ONNX runtime needs
no separate download.

## Licensing

| Path | Licence |
|---|---|
| `hardware/` | CERN-OHL-S v2 |
| everything else | MIT (see `LICENSE`) |
| dataset and log, on Zenodo | CC BY 4.0 |

## Citation

See `CITATION.cff`.

## Authors

**Muh Yuzril Ihza Baharuddin** — main researcher and developer
**Prof. Dr. Birol Elevli**, Ondokuz Mayıs Üniversitesi — academic supervisor

Part of a Master's thesis on real-time industrial quality control, *Derin Öğrenme ve
Üretim Yürütme Sistemi (ÜYS)*.
