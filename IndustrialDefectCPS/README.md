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
```
#### 2. Model Weights Placement
Take your best-performing model weights file (best.pt) obtained from your custom YOLOv8m-seg training sessions.

Place the best.pt file directly into the main project root directory (at the exact same level as your execution scripts).

Open final.py and verify that the model path parameter points precisely to this file's location.

#### 3. Software Dependencies Installation
With your virtual environment activated, install the required libraries by running the following command in your terminal:

```bash
pip install opencv-python ultralytics pyserial numpy tqdm dash requests 
```
Technical Note: Core libraries such as os, time, random, string, and collections are built directly into Python and do not require additional installation steps.

#### 4. Microcontroller Configuration & Flashing
Open the microcontroller firmware script plc_system.ino using the Arduino IDE or PlatformIO.

To prevent compilation errors, open the Library Manager and install the Adafruit PWM Servo Driver library.

Connect your ESP32 microcontroller to your computer via a reliable data/USB cable, verify the source code, and upload/flash the firmware onto the device.

### PHASE 2: Hardware Configuration & Connection Management
#### 1. Physical Power Initialization
Ensure that the entire electrical and power distribution framework is turned on and fully stable. Check power connections for:

The mechanical conveyor unit

Laptop / HPC local server

External operator monitor

Industrial camera interface

External power adapters for the servo driver modules

#### 2. Hardware Port Verification & Mapping
Establish your physical connections systematically according to the parameters and operational procedures below:

Microcontroller to Laptop (Serial Communication):

Connect the ESP32 using a high-quality USB-C cable.

Critical Step: Identify the dynamically assigned port ID by opening Device Manager (Windows) or running ls /dev/tty* (Linux/macOS) (e.g., COM3 or /dev/ttyUSB0).

Open your final.py script and modify the serial.Serial() initialization parameter to match this exact port ID.

Camera to Laptop (Perceptual Input):

Connect the industrial camera to a USB port utilizing an HDMI Video Capture Card (USB-HDMI adapter) to stream the external video feed.

Critical Step: Because laptops feature built-in webcams (typically assigned index 0), you must verify and adjust the camera capture index inside final.py (e.g., cv2.VideoCapture(index) usually shifts to index 1 or 2).

External Monitor to Laptop:

Connect an additional monitor using an available DisplayPort, HDMI, or VGA-to-HDMI adapter to expand the visual workspace for the operator's interface dashboard.

### PHASE 3: IoT Infrastructure Activation & System Launch
To guarantee seamless interaction between the deep learning model inference, the user dashboard, and the autonomous reporting tools, you must execute the program in the following exact order:

#### 1. Initialize the IoT Agent Ecosystem (Docker & n8n)
Ensure that the Docker Desktop application is running in the background.

Activate your local n8n container instance to prepare the system's webhook ingestion pathway.

#### 2. Establish Network Tunneling (ngrok)
Open a brand new terminal window and run an ngrok tunnel command to securely expose your local n8n workflow port to the public web environment:

```bash
ngrok http 5678
```
(Note: Modify port 5678 if your custom local n8n instance architecture utilizes a different port configuration).

#### 3. Run the Core System Application
Once the hardware links, Docker containers, and ngrok endpoints are fully initialized, launch the main processing script from your primary virtual environment terminal:

```bash
python final.py
```
🛑 Important Integration Notes
Advanced IoT & n8n Automation
The advanced data logging framework and autonomous report generation system within this project are orchestrated by an n8n-based IoT Agent executing in a Docker environment.

[!CAUTION]
Because the underlying webhook structure and n8n workflow node configurations feature highly complex architectural parameters, future researchers or developers aiming to replicate or modify this automation framework are strongly advised to refer to the Separate Workflow Documentation or contact the main system developer directly.

👥 Authors & Acknowledgments

Main Researcher/Developer: MUH YUZRIL IHZA BAHARUDDIN

Academic Supervisor: Prof. Dr. Birol Elevli (Ondokuz Mayıs Üniversitesi)

Project Context: Part of the Master's Thesis project focused on real-time industrial quality control: "Derin Öğrenme ve Üretim Yürütme Sistemi (ÜYS)".
