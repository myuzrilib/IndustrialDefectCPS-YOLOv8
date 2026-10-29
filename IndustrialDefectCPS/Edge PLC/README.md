# Firmware — ESP32

`plc_system/plc_system.ino`

Reads a single-character class identifier from USB serial at 115,200 baud, turns the
corresponding arm to 90° through the PCA9685, holds it for `INTERVAL_DORONG` (5,000 ms),
and returns it to 0°.

On reset it cycles all four arms as a self-test. Use that to confirm channel order and
mechanical clearance before putting anything on the belt.

## Signals

The host sends one byte per decision. The mapping is in `final.py`:

| Byte | Station | Distance from camera |
|---|---|---|
| `1` | A | 0.50 m |
| `2` | B | 1.00 m |
| `3` | C | 1.50 m |
| `4` | D | 2.00 m |

Two quality grades share station D, so four stations serve five grades.

## Wiring

| ESP32 | PCA9685 |
|---|---|
| GPIO 21 | SDA |
| GPIO 22 | SCL |

Servo signal lines go to PCA9685 channels 0–3 **in station order**. See
`../../hardware/wiring.png` for the full schematic.

Power the servos from a dedicated supply rail sized for four MG995 units under
simultaneous stall — **not** from the ESP32 regulator. Tie the grounds together. The USB
link carries both microcontroller power and the serial command channel.

## Dependencies

`Adafruit_PWMServoDriver` and `Wire`. A copy of the Adafruit library is included here as
a zip for offline installation.

## The hold interval

`INTERVAL_DORONG` is a software constant, not a mechanical limit — the MG995 is rated at
0.20 s per 60°. The 5,000 ms value is what gives the cell its tolerance to timing error;
reducing it raises the throughput ceiling and narrows the window a component has to hit.
