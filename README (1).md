# 🎯 Arduino Radar Monitor

A real-time radar scanner built with Arduino + Python. An ultrasonic sensor mounted on a servo motor sweeps 180° and displays detected objects on a live radar monitor on your PC.

![Radar Demo](screenshot.png)
> *(Add a screenshot or GIF of your radar running here)*

---

## 📋 How It Works

The HC-SR04 ultrasonic sensor is mounted on a SG90 servo motor. The servo sweeps from 0° to 180° and back, measuring distance at each angle. The Arduino sends angle and distance data over USB serial to the PC, where a Python script renders it as a live radar display.

---

## 🔧 Hardware Required

| Component | Price (approx) |
|---|---|
| Arduino Uno | ~8€ |
| HC-SR04 Ultrasonic Sensor | ~1.5€ |
| SG90 Servo Motor | ~2.5€ |
| Breadboard + Jumper Wires | ~3€ |
| **Total** | **~15€** |

---

## 🔌 Wiring

**HC-SR04 Ultrasonic Sensor:**
```
VCC  → Arduino 5V
GND  → Arduino GND
TRIG → Arduino Pin 10
ECHO → Arduino Pin 11
```

**SG90 Servo Motor:**
```
Red   (VCC)    → Arduino 5V
Brown (GND)    → Arduino GND
Orange (Signal) → Arduino Pin 9
```

---

## 💻 Software Setup

### 1. Arduino
- Install [Arduino IDE](https://www.arduino.cc/en/software)
- Open `radar_arduino.ino`
- Upload to your Arduino board

### 2. Python
Make sure Python 3 is installed, then:
```bash
pip install pyserial
```
> Note: Uses **tkinter** for the display (built into Python — no extra install needed)

---

## 🚀 Running the Radar

1. Connect Arduino via USB
2. Check which COM port it's using: Arduino IDE → Tools → Port
3. Edit `radar.py` and change:
```python
PORT = "COM3"  # change to your port (e.g. COM4, COM5...)
```
4. Run:
```bash
python radar.py
```

---

## 🖥️ Radar Monitor Features

- 🟢 Animated sweep line with glow effect
- 🔴 Line tracing detected objects — fades over 8 seconds
- Distance rings at 50cm / 100cm / 150cm / 200cm
- Angle markers every 15°
- Live status panel (angle, distance, port, scan status)
- Configurable max detection range

---

## ⚙️ Configuration

In `radar.py`, you can adjust:
```python
PORT     = "COM3"   # Serial port
MAX_DIST = 50       # Detection range in cm
```

In `radar_arduino.ino`, you can adjust:
```cpp
// Sweep speed — lower = faster but less accurate
delay(30);
```

---

## 📁 Project Structure

```
arduino-radar/
├── radar_arduino.ino   # Arduino sketch
├── radar.py            # Python radar display
└── README.md
```

---

## 🛠️ Built With

- [Arduino](https://www.arduino.cc/)
- [Python 3](https://www.python.org/)
- [pyserial](https://pypi.org/project/pyserial/)
- tkinter (Python built-in)

---

## 📄 License

MIT License — free to use, modify and share.
