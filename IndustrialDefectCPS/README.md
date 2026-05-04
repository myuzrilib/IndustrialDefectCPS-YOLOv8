# Industrial Defect CPS - YOLOv8s-seg (93.8% mAP@0.5)

Low-cost ($1543) Cyber-Physical System for real-time defect sorting.

yolo segment predict model=models/best.onnx

# Dataset Info

- **Total**: 1331 images (proxy spherical defects)
- **Classes**: 6 (cok_iyi, cok_kotu, curuk, iyi_cig, kusur, yari_iyi)
- **Split**: Train 999 (75%), Val 173 (13%), Test 159 (12%)
- **Format**: COCO Segmentation JSON
- **Full dataset**: https://doi.org/10.5281/zenodo.19928743

## 📊 Key Results

- **mAP@0.5**: 93.8% (6 classes)
- **mAP50-95**: 89.0%
- **Edge FPS**: 1.65 (ESP32-S3)
- **Dataset**: [Zenodo DOI](https://doi.org/10.5281/zenodo.19928743)

## 🏗️ Structure
