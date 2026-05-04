#!/usr/bin/env python3
"""
YOLOv8s-seg INDUSTRIAL CPS - FINAL VERSION
Path: /home/yuzril/project/task1/objek-kusur-tespiti-10/
Sophie Supercomputer Optimized
"""

import os
from ultralytics import YOLO

# =====================================================
# FIXED PATH - NO EDIT NEEDED
# =====================================================
DATA_PATH = "/home/yuzril/project/task1/objek-kusur-tespiti-10"
PROJECT_NAME = "cps_yolov8s_industrial_v2"
EPOCHS = 150
BATCH_SIZE = 32

def main():
    print("🚀 CPS YOLOv8s TRAINING - SOPHIE SUPERCOMPUTER")
    print(f"📁 Dataset: {DATA_PATH}")
    
    # VERIFY DATASET
    data_yaml = f"{DATA_PATH}/data.yaml"
    assert os.path.exists(data_yaml), f"❌ {data_yaml} not found!"
    
    train_count = len(os.listdir(f"{DATA_PATH}/train/images"))
    val_count = len(os.listdir(f"{DATA_PATH}/valid/images"))
    print(f"✅ Train: {train_count} images, Val: {val_count} images")
    
    # 1. LOAD MODEL
    print("\n📥 Loading yolov8s-seg.pt...")
    model = YOLO('yolov8s-seg.pt')
    
    # 2. TRAINING CONFIG (Copy-paste ready metrics)
    config = {
        'data': data_yaml,
        'epochs': EPOCHS,
        'imgsz': 640,
        'batch': BATCH_SIZE,
        'workers': 16,
        'device': 0,
        'project': f'runs/seg/{PROJECT_NAME}',
        'name': 'train',
        
        # INDUSTRIAL AUGMENTATION
        'hsv_h': 0.02, 'hsv_s': 0.8, 'hsv_v': 0.4,
        'degrees': 10.0, 'translate': 0.1, 'scale': 0.7,
        'shear': 2.0, 'perspective': 0.0002, 'flipud': 0.0, 'fliplr': 0.5,
        'mosaic': 1.0, 'mixup': 0.1, 'copy_paste': 0.1,
        
        # OPTIMIZER
        'optimizer': 'AdamW', 'lr0': 0.001, 'lrf': 0.01,
        'momentum': 0.937, 'weight_decay': 0.0005,
        
        'save': True, 'save_period': 25, 'patience': 20,
    }
    
    print("\n🔥 TRAINING STARTED...")
    results = model.train(**config)
    
    # 3. FINAL METRICS
    print("\n📊 FINAL VALIDATION...")
    val_results = model.val()
    
    # 4. PUBLICATION METRICS
    metrics = {
        'map50_box': val_results.box.map50,
        'map_box': val_results.box.map,
        'map50_mask': val_results.seg.map50,
        'precision': val_results.box.mp,
        'recall': val_results.box.mr,
    }
    
    print("\n" + "="*80)
    print("🎉 PUBLICATION-READY METRICS (Copy ke reviewer):")
    print("="*80)
    for key, value in metrics.items():
        print(f"{key:15}: {value:7.3f}%")
    print(f"Model: runs/seg/{PROJECT_NAME}/weights/best.pt")
    print(f"Dataset DOI: https://doi.org/10.5281/zenodo.19928743")
    print("="*80)
    
    # 5. EXPORT
    print("\n🔄 Edge deployment export...")
    model.export(format='onnx', imgsz=640, simplify=True)
    
    # 6. SAVE SUMMARY
    with open('IEEE_TII_METRICS.txt', 'w') as f:
        f.write(f"YOLOv8s-seg v2\n")
        for k, v in metrics.items():
            f.write(f"{k}: {v:.3f}%\n")
    
    print("\n✅ COMPLETE! Check IEEE_TII_METRICS.txt")
    print("\n📤 Kirim output ini ke AI Mentor:")

if __name__ == "__main__":
    main()