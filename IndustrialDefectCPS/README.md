# Cyber-Physical System (CPS) Based Automatic Sorting System

This repository contains the systematic procedures and source code to configure, deploy, and execute a **Cyber-Physical System (CPS) Based Automatic Sorting System**. The architecture integrates a deep learning model (YOLOv8m-seg), microcontroller serial communication, and an automated IoT Agent framework.

---

## System Architecture Overview

1. **AI Perception Layer:** Real-time object detection and segmentation powered by `YOLOv8m-seg`.
2. **Hardware Control Layer:** ESP32 microcontroller coordinating conveyor mechanics and servo modules.
3. **IoT Integration Layer:** Automated data pipelines and reporting via Dockerized `n8n` instances exposed through secure `ngrok` tunnels.

---

## Prerequisites & Installation

### Phase 1: Workspace Setup & Software Dependencies

#### 1. Environment Isolation
Open the project root directory in your preferred IDE (e.g., VSCode) and initialize a Python virtual environment to avoid dependency conflicts. Additionally, create a local directory named `/frames` to temporarily store inference outputs (bounding boxes & segmentation masks).
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Create output frames directory
mkdir frames
