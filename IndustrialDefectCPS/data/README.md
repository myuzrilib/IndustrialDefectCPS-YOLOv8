# Dataset configuration

`data.yaml` — the Ultralytics dataset descriptor used for training.

The images themselves are not in this repository. Full dataset, annotations and the raw
session log: [10.5281/zenodo.19928743](https://doi.org/10.5281/zenodo.19928743)

## Partitions

665 original images of proxy spherical defects, split **333 / 173 / 159 before
augmentation**. The training partition is then augmented threefold, giving the
999 / 173 / 159 that `data.yaml` describes.

Splitting before augmenting is what keeps augmented copies of a training image out of the
validation and test partitions.

Annotations are COCO segmentation polygons.

## Classes

`nc: 6`

| Class | Role |
|---|---|
| `cok iyi` | quality grade |
| `yari iyi` | quality grade |
| `iyi cig` | quality grade |
| `curuk` | quality grade |
| `cok kotu` | quality grade |
| `kusur` | defect region — not a sorting target |

Five grades, four physical stations: two grades share the station at 2.00 m. The mapping
from class to station lives in `../inference/final.py`.

## A note on the reported mAP

The headline mAP is a mean across all six categories, which differ in difficulty — the
defect-region category is not a quality grade. It is therefore not directly comparable to
a five-class grading accuracy. Per-class mAP was not reported separately.

## `path`

`data.yaml` carries an absolute path from the machine the model was trained on. Change it
to your own dataset root before training.
