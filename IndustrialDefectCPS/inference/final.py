import cv2
import csv
import os
import time
import random
import string
import numpy as np
from collections import deque
from ultralytics import YOLO
import serial

# ========================
# 1. KONFIGURASI SISTEM
# ========================
MODEL_PATH = "best.pt"
CSV_FILE = "tespiti_log.csv"
FRAMES_DIR = "frames"
SERIAL_PORT = 'COM9'
BAUD_RATE = 115200

# --- KONFIGURASI TRIGGER CAHAYA (GLARE) ---
TRIGGER_BOX_WIDTH = 600    # Saya perlebar sedikit ke 200 agar lebih mudah menangkap
BRIGHTNESS_THRESHOLD = 100 # Ambang batas cahaya (0-255). 220 = Putih sangat terang.
MIN_GLARE_AREA = 500       # Ukuran minimal pantulan cahaya (agar noise tidak memicu)
COOLDOWN_TIME = 2.0        # Waktu istirahat setelah trigger

# --- FISIKA KONVEYOR & SERVO ---
CONVEYOR_SPEED = 0.054   # m/s, measured on the belt. Commanded delays scale with this.
OFFSET_METERS = 0.30     

DISTANCES = {
    "Optimal Quality":  0.50,
    "Severe Defect": 1.00,
    "Unprocessed":  1.50,
    "Moderate Defect":    2.00,
    "Critical Anomaly": 2.00
}

SERVO_SIGNALS = {
    "Optimal Quality":  b'1',
    "Severe Defect": b'2',
    "Unprocessed":  b'3',
    "Moderate Defect":    b'4',
    "Critical Anomaly": b'4'
}

# ---------------------------------------------------------------------------
# The trained weights label their classes in Turkish (see data.yaml); the logic
# below is written against English names. This table bridges the two.
#
# VERIFY THESE FIVE PAIRINGS BEFORE RUNNING ON HARDWARE. A wrong pairing sends a
# component to the wrong bin silently, which is worse than no detection at all.
# "kusur" marks a defect region rather than a quality grade and is not a sorting
# target, so it maps to None.
# ---------------------------------------------------------------------------
CLASS_TRANSLATION = {
    "cok iyi":  "Optimal Quality",
    "cok kotu": "Severe Defect",
    "iyi cig":  "Unprocessed",
    "yari iyi": "Moderate Defect",
    "curuk":    "Critical Anomaly",
    "kusur":    None,
}


def translate(label):
    """Map a model class name to a sorting label, or None if it is not a target."""
    if label in CLASS_TRANSLATION:
        return CLASS_TRANSLATION[label]
    if label in SERVO_SIGNALS:          # already an English sorting label
        return label
    raise KeyError(
        f"model class {label!r} is not in CLASS_TRANSLATION. Add it, or the "
        f"component it describes will never be sorted."
    )


subclass_map = {
    "Optimal Quality": "A",
    "Severe Defect": "B",
    "Unprocessed": "C",
    "Moderate Defect": "D",
    "Critical Anomaly": "D"
}

# ========================
# 2. INISIALISASI
# ========================
os.makedirs(FRAMES_DIR, exist_ok=True)
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Class", "Cumulative_Count", "Code", "Sub_Class"])

print(f"Loading model from {MODEL_PATH}...")
model = YOLO(MODEL_PATH)

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    print(f"Berhasil terhubung ke ESP32 di {SERIAL_PORT}")
    time.sleep(2)
except Exception:
    print("Mode OFFLINE (Serial tidak terhubung)")
    ser = None

cumulative_counts = {k: 0 for k in subclass_map.keys()}
used_codes = set()
task_queue = deque()
last_trigger_timestamp = 0 

def generate_unique_code():
    while True:
        rand_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        kode = f"Z{rand_part}"
        if kode not in used_codes:
            used_codes.add(kode)
            return kode

# Setup Kamera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
# PENTING: Exposure rendah membantu mengurangi silau dan motion blur
# cap.set(cv2.CAP_PROP_EXPOSURE, -4) 

cv2.namedWindow("Sistem Sorting Tesis", cv2.WINDOW_NORMAL)

# Atur Tampilan
screen_width = 1920  
screen_height = 1080 
scale = 0.80        
new_width = int(screen_width * scale)
new_height = int(screen_height * scale)
cv2.resizeWindow("Sistem Sorting Tesis", new_width, new_height)
cv2.moveWindow("Sistem Sorting Tesis", 100, 50)

print(f"Sistem Siap. Trigger: PANTULAN CAHAYA DI TENGAH LAYAR.")

# ========================
# 3. LOOP UTAMA
# ========================
try:
    while True:
        ret, frame = cap.read()
        if not ret: break

        height, width, _ = frame.shape
        current_time = time.time()
        
        # ----------------------------------------------------
        # A. BUAT ZONA TRIGGER & VISUALISASI
        # ----------------------------------------------------
        center_x = width // 2
        trigger_x1 = center_x - (TRIGGER_BOX_WIDTH // 2)
        trigger_x2 = center_x + (TRIGGER_BOX_WIDTH // 2)
        trigger_y1 = 0
        trigger_y2 = height

        # Visualisasi Kotak Trigger
        cv2.rectangle(frame, (trigger_x1, trigger_y1), (trigger_x2, trigger_y2), (255, 0, 0), 2)
        cv2.putText(frame, "TRIGGER ZONE", (trigger_x1, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        # ----------------------------------------------------
        # B. DETEKSI POSISI CAHAYA (GLARE)
        # ----------------------------------------------------
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, BRIGHTNESS_THRESHOLD, 255, cv2.THRESH_BINARY)
        
        # DEBUG VIEW
        thresh_debug = cv2.resize(thresh, (300, 200))
        cv2.imshow("DEBUG VIEW", thresh_debug)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        glare_detected = False
        
        if contours:
            max_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(max_contour)
            
            if area > MIN_GLARE_AREA:
                M = cv2.moments(max_contour)
                if M["m00"] != 0:
                    glare_center_x = int(M["m10"] / M["m00"])
                    glare_center_y = int(M["m01"] / M["m00"])
                    cv2.circle(frame, (glare_center_x, glare_center_y), 15, (0, 0, 255), -1)
                    
                    if trigger_x1 < glare_center_x < trigger_x2:
                        glare_detected = True

        # ----------------------------------------------------
        # C. LOGIKA UTAMA (TRIGGER & CAPTURE)
        # ----------------------------------------------------
        
        # STATUS 1: COOLDOWN
        if (current_time - last_trigger_timestamp) < COOLDOWN_TIME:
            sisa = COOLDOWN_TIME - (current_time - last_trigger_timestamp)
            cv2.putText(frame, f"WAIT: {sisa:.1f}s", (50, height - 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            cv2.rectangle(frame, (trigger_x1, trigger_y1), (trigger_x2, trigger_y2), (0, 255, 255), 4)

        # STATUS 2: TRIGGER AKTIF
        elif glare_detected:
            print(">>> [TRIGGER] Cahaya masuk zona! Deteksi dimulai...")
            
            results = model.predict(frame, conf=0.5, verbose=False)
            
            detected_class = None
            max_conf = 0
            
            if results[0].boxes:
                for box in results[0].boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    label = translate(model.names[cls_id])
                    if label is None: continue
                    
                    if label == "background" or label == "0": continue 

                    # Prioritas Cacat
                    if label in ["Moderate Defect", "Critical Anomaly", "Unprocessed"]:
                        detected_class = label
                        max_conf = conf
                        break 
                    
                    if conf > max_conf:
                        max_conf = conf
                        detected_class = label

            # JIKA OBJEK VALID DITEMUKAN
            if detected_class and detected_class in subclass_map:
                print(f"    HASIL: {detected_class} ({max_conf:.2f})")
                
                # 1. Update Data & Cooldown
                last_trigger_timestamp = current_time
                cumulative_counts[detected_class] += 1
                kode = generate_unique_code()
                
                # 2. Simpan Foto
                filename = f"{FRAMES_DIR}/{detected_class}_{kode}_{time.strftime('%H%M%S')}.jpg"
                cv2.imwrite(filename, frame)

                # ==========================================
                # [PERBAIKAN] SIMPAN KE CSV (DENGAN CEK ERROR)
                # ==========================================
                # ==========================================
                # [PERBAIKAN TOTAL] SIMPAN KE CSV
                # ==========================================
                try:
                    sub_class = subclass_map[detected_class]
                    timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Debugging di Terminal: Pastikan variabel TIDAK kosong sebelum ditulis
                    # Jika di terminal muncul "None", berarti masalah ada di logika deteksi, bukan CSV.
                    print(f"    [DEBUG DATA] Time:{timestamp_str} | Class:{detected_class} | Count:{cumulative_counts[detected_class]}")

                    # Buka file dengan mode 'a' (append) dan encoding utf-8
                    with open(CSV_FILE, mode="a", newline="", encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            timestamp_str,
                            detected_class,
                            cumulative_counts[detected_class],
                            kode,
                            sub_class
                        ])
                        
                        # --- SOLUSI UTAMA: PAKSA TULIS KE DISK ---
                        f.flush()            # Dorong dari memori Python ke OS
                        os.fsync(f.fileno()) # Dorong dari OS ke Harddisk Fisik
                        # -----------------------------------------
                        
                    print(f"    [CSV] SUKSES TERSIMPAN: Baris baru ditambahkan.")
                    
                except Exception as e:
                    print(f"\n[!!! ERROR CSV !!!] Gagal menyimpan: {e}\n")
                # ==========================================
                # ==========================================
                
                # 4. Jadwalkan Servo
                if detected_class in DISTANCES:
                    jarak_total = DISTANCES[detected_class]
                    jarak_trigger = jarak_total - OFFSET_METERS
                    if jarak_trigger < 0: jarak_trigger = 0 
                    
                    waktu_tunggu = jarak_trigger / CONVEYOR_SPEED
                    trigger_time = current_time + waktu_tunggu
                    signal_bytes = SERVO_SIGNALS.get(detected_class)
                    
                    task = {'trigger_time': trigger_time, 'signal': signal_bytes, 'info': f"{detected_class}"}
                    task_queue.append(task)
            
            # Ubah warna kotak jadi Hijau
            cv2.rectangle(frame, (trigger_x1, trigger_y1), (trigger_x2, trigger_y2), (0, 255, 0), 10)

        # ----------------------------------------------------
        # EKSEKUTOR SERVO
        # ----------------------------------------------------
        now = time.time()
        pending_tasks = list(task_queue)
        for task in pending_tasks:
            if now >= task['trigger_time']:
                if ser and task['signal']:
                    ser.write(task['signal'])
                    print(f"==> [SERVO] Action: {task['info']}")
                task_queue.remove(task)

        # ----------------------------------------------------
        # TAMPILAN UI
        # ----------------------------------------------------
        font = cv2.FONT_HERSHEY_SIMPLEX
        y_pos = 60
        cv2.putText(frame, "STATUS SORTIR:", (30, y_pos), font, 1, (255, 255, 255), 2)
        y_pos += 40
        for c_name, count in cumulative_counts.items():
            text = f"{c_name.upper()}: {count}"
            cv2.putText(frame, text, (30, y_pos), font, 0.8, (0, 255, 255), 2)
            y_pos += 30

        cv2.imshow("Sistem Sorting Tesis", frame)
        
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q') or key == 27:
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    if ser: ser.close()