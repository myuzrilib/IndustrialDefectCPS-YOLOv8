#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// === KONFIGURASI SERVO MG995 ===
#define SERVO_FREQ 50 

// Kalibrasi Pulse
#define SERVOMIN  120 // Posisi 0 derajat (Tutup)
#define SERVOMAX  500 // Posisi 180 derajat (Max teoritis)
#define SERVO_90  310 // Posisi 90 derajat (Titik Tengah)

// Mapping Port Servo
const int SERVO_PORTS[4] = {0, 1, 2, 3}; 

// Variabel Timer
int servoState[4] = {0, 0, 0, 0};      
unsigned long servoTimer[4] = {0, 0, 0, 0};
const long INTERVAL_DORONG = 2000; // Jeda 2 Detik

void setup() {
  Serial.begin(115200);
  Serial.println("\n--- SYSTEM BOOTING ---");

  Wire.begin(21, 22);
  
  pwm.begin();
  pwm.setOscillatorFrequency(27000000);
  pwm.setPWMFreq(SERVO_FREQ);

  delay(100);

  // 1. Pastikan posisi awal SEMUA tertutup dulu
  for(int i=0; i<4; i++){
      pwm.setPWM(SERVO_PORTS[i], 0, SERVOMIN);
  }

  // ======================================================
  // FITUR: GERAKAN SELF-TEST SAAT RESET
  // ======================================================
  Serial.println(">>> Melakukan Self-Test Servo (Cek Gerakan)...");
  
  // Panggil fungsi gerakan pembuka
  testAllServos(); 
  
  Serial.println(">>> Self-Test Selesai. Sistem Siap & Menunggu Python.");
}

void loop() {
  // --- BAGIAN 1: BACA DATA DARI PYTHON ---
  if (Serial.available() > 0) {
    char signal = Serial.read();
    if (signal == '\n' || signal == '\r' || signal == ' ') return;

    int servoIndex = -1;
    if (signal == '1') servoIndex = 0;      
    else if (signal == '2') servoIndex = 1; 
    else if (signal == '3') servoIndex = 2; 
    else if (signal == '4') servoIndex = 3; 

    if (servoIndex != -1) {
      // Gerak ke 90 Derajat
      pwm.setPWM(SERVO_PORTS[servoIndex], 0, SERVO_90);
      
      servoState[servoIndex] = 1;       
      servoTimer[servoIndex] = millis(); 
      
      Serial.print("[ESP32] Servo "); 
      Serial.print(servoIndex + 1); 
      Serial.println(" OPEN (90 Derajat)");
    }
  }

  // --- BAGIAN 2: AUTO CLOSE (2 DETIK) ---
  unsigned long currentMillis = millis();
  
  for(int i=0; i<4; i++) {
    if (servoState[i] == 1) {
      if (currentMillis - servoTimer[i] >= INTERVAL_DORONG) {
        pwm.setPWM(SERVO_PORTS[i], 0, SERVOMIN); // Kembali ke 0
        servoState[i] = 0; 
        Serial.print("[ESP32] Servo "); 
        Serial.print(i + 1); 
        Serial.println(" CLOSE (0 Derajat)");
      }
    }
  }
}

// ======================================================
// FUNGSI TEST (Dijalankan saat Setup/Reset)
// ======================================================
void testAllServos() {
  // Gerakkan servo satu per satu (Wave Effect)
  for (int i=0; i<4; i++) {
    Serial.print("Testing Servo "); Serial.println(i+1);
    
    // 1. Buka ke 90
    pwm.setPWM(SERVO_PORTS[i], 0, SERVO_90);
    delay(300); // Tunggu sebentar biar kelihatan geraknya
    
    // 2. Tutup ke 0
    pwm.setPWM(SERVO_PORTS[i], 0, SERVOMIN);
    delay(300); // Jeda sebelum lanjut ke servo berikutnya
  }
  
  // Berikan sinyal kedip cepat (buka tutup cepat semua) sebagai tanda akhir
  delay(500);
  // (Opsional: Jika ingin semua gerak sedikit barengan di akhir)
  /*
  for(int i=0; i<4; i++) pwm.setPWM(SERVO_PORTS[i], 0, 200); // Buka dikit
  delay(200);
  for(int i=0; i<4; i++) pwm.setPWM(SERVO_PORTS[i], 0, SERVOMIN); // Tutup
  */
}