# Training

`yolov8s.py` — the training script, with the hyperparameters that produced the deposited
weights.

| | |
|---|---|
| Architecture | YOLOv8s-seg |
| Epochs | 150, patience 20 |
| Batch | 32 |
| Image size | 640 px |
| Optimiser | AdamW, lr0 0.001, lrf 0.01, weight decay 0.0005 |
| Augmentation | HSV, ±10° rotation, 0.7 scale, 2° shear, mosaic, mixup 0.1, copy-paste 0.1, horizontal flip |

Edit `DATA_PATH` to point at your dataset root — it is an absolute path from the machine
the model was trained on — then:

```bash
python yolov8s.py
```

The script validates, prints the publication metrics, and exports an ONNX copy of the
weights as its final step.

## Results

| | |
|---|---|
| mAP@0.5 | 93.8% |
| mAP@0.5:0.95 | 89.0% |

## `best.pt/best.pt`

The trained checkpoint, 23.9 MB. This is what `../inference/final.py` loads and what every
reported figure was measured with. Its class names are the six Turkish labels from
`../data/data.yaml`.

An ONNX export is **not** committed separately: it is a format conversion of this file,
written by `yolov8s.py`, so a builder who prefers that runtime regenerates it in one
command rather than downloading a second artefact.
