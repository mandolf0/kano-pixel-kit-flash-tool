# Kano Pixel Kit - ESP32 Hardware & MicroPython Guide

## Hardware Specs

| Component | Specification |
|-----------|---------------|
| **SoC** | Espressif ESP32 |
| **CPU** | Dual-core Xtensa LX6 @ 240MHz |
| **RAM** | ~70KB free after MicroPython + Pixel32 |
| **Flash** | 4MB |
| **Platform** | esp32 |
| **MicroPython** | 3.4.0 (v1.9.4, May 2018 build) |

## Display

| Specification | Value |
|---------------|-------|
| **Type** | WS2812B NeoPixel LED Matrix |
| **Resolution** | 16 x 8 (128 LEDs) |
| **Colors** | 24-bit RGB (16.7 million colors) |
| **GPIO Pin** | 4 |

Coordinate system:
```
(0,0) -----> (15,0)   X-axis
  |
  |
  v
(0,7) -----> (15,7)   Y-axis
```

## Inputs

### Buttons

| Button | GPIO Pin | Type |
|--------|----------|------|
| Button A | 23 | Digital, active low |
| Button B | 18 | Digital, active low |

### Joystick (5-way)

| Direction | GPIO Pin | Type |
|-----------|----------|------|
| Up | 35 | Digital, active low |
| Down | 34 | Digital, active low |
| Left | 26 | Digital, active low |
| Right | 25 | Digital, active low |
| Click (center) | 27 | Digital, active low |

### Dial (Potentiometer)

| Component | GPIO Pin | Type |
|-----------|----------|------|
| Dial | 36 | Analog (ADC), 12-bit |
| Range | 0 - 4095 | |

---

## Software Stack

### What's Running

After flashing with this tool, the Pixel Kit runs:

1. **MicroPython** (v1.9.4) - Python interpreter for microcontrollers
2. **Pixel32** (v0.2.3) - Kano's library for the Pixel Kit hardware

### Files on Device

```
boot.py          # Runs on boot
main.py          # Main application (runs after boot.py)
PixelKit.py      # Hardware abstraction library
PixelTurtle.py   # Turtle graphics library
wifi.py          # WiFi configuration
microWebSrv.py   # Built-in web server
microDNSSrv.py   # DNS server for captive portal
webrepl_cfg.py   # WebREPL configuration
index.html       # Web interface
```

---

## Getting Started

### Connecting via Serial

```bash
# Install pyserial
pip install pyserial

# Connect (Linux)
screen /dev/ttyUSB0 115200

# Or use Python
python -c "import serial; s=serial.Serial('/dev/ttyUSB0', 115200); s.write(b'\r\n')"
```

### Basic REPL Commands

```python
# Import the library
import PixelKit as pk

# Check memory
import gc
gc.collect()
print(gc.mem_free())  # ~70KB free
```

---

## LED Matrix

### Basic Operations

```python
import PixelKit as pk

# Set a single pixel (x, y, (r, g, b))
pk.set_pixel(0, 0, (255, 0, 0))    # Red at top-left
pk.set_pixel(15, 7, (0, 255, 0))   # Green at bottom-right

# Must call render() to display changes!
pk.render()

# Set background color for all pixels
pk.set_background((0, 0, 50))      # Dim blue background
pk.render()

# Clear all pixels
pk.clear()
pk.render()
```

### Drawing Patterns

```python
import PixelKit as pk

# Horizontal line
for x in range(16):
    pk.set_pixel(x, 4, (255, 255, 0))  # Yellow line

# Vertical line
for y in range(8):
    pk.set_pixel(8, y, (0, 255, 255))  # Cyan line

pk.render()

# Fill entire screen
for x in range(16):
    for y in range(8):
        pk.set_pixel(x, y, (255, 0, 255))  # Magenta
pk.render()

# Rainbow effect
import time
colors = [
    (255,0,0), (255,127,0), (255,255,0), (0,255,0),
    (0,255,255), (0,0,255), (127,0,255), (255,0,127)
]
for y in range(8):
    for x in range(16):
        pk.set_pixel(x, y, colors[y])
pk.render()
```

### Animation Example

```python
import PixelKit as pk
import time

# Moving dot
for x in range(16):
    pk.clear()
    pk.set_pixel(x, 4, (255, 255, 255))
    pk.render()
    time.sleep(0.1)
```

---

## Reading Inputs

### Buttons

```python
import PixelKit as pk

# Must call check_controls() first to update state!
pk.check_controls()

# Read button states (True = pressed)
if pk.is_pressing_a:
    print("Button A pressed!")

if pk.is_pressing_b:
    print("Button B pressed!")
```

### Joystick

```python
import PixelKit as pk

pk.check_controls()

# Read joystick (True = pressed in that direction)
if pk.is_pressing_up:
    print("Up!")
if pk.is_pressing_down:
    print("Down!")
if pk.is_pressing_left:
    print("Left!")
if pk.is_pressing_right:
    print("Right!")
if pk.is_pressing_click:
    print("Joystick clicked!")
```

### Dial (Potentiometer)

```python
import PixelKit as pk

# Read analog value (0-4095)
value = pk.dial.read()
print("Dial:", value)

# Map to 0-15 for X position
x = value * 15 // 4095

# Map to brightness (0-255)
brightness = value * 255 // 4095
```

---

## Complete Example: Interactive Demo

```python
import PixelKit as pk
import time

# Color controlled by dial, position by joystick
x, y = 8, 4  # Start in center

while True:
    pk.check_controls()

    # Move with joystick
    if pk.is_pressing_up and y > 0:
        y -= 1
    if pk.is_pressing_down and y < 7:
        y += 1
    if pk.is_pressing_left and x > 0:
        x -= 1
    if pk.is_pressing_right and x < 15:
        x += 1

    # Dial controls color hue
    dial = pk.dial.read()
    r = (dial * 255) // 4095
    g = 255 - r
    b = 128

    # Button A = clear, Button B = fill
    if pk.is_pressing_a:
        pk.clear()
    if pk.is_pressing_b:
        pk.set_background((r, g, b))

    # Draw cursor
    pk.set_pixel(x, y, (255, 255, 255))
    pk.render()

    time.sleep(0.05)
```

---

## WiFi & WebREPL

The Pixel32 firmware includes a web interface:

```python
import wifi

# Connect to existing network
wifi.connect('YourSSID', 'YourPassword')

# Or check wifi.py for AP mode configuration
```

Once connected, you can use WebREPL to program wirelessly.

---

## Useful Modules

```python
# Available standard MicroPython modules
import machine    # Hardware access (pins, PWM, I2C, SPI)
import time       # sleep, ticks_ms, etc.
import gc         # Garbage collection
import os         # File system operations
import sys        # System info
import network    # WiFi

# Pixel Kit specific
import PixelKit      # LED matrix and inputs
import PixelTurtle   # Turtle graphics
```

---

## Uploading Files to Device

Use `ampy` to upload MicroPython scripts to the device:

```bash
pip install adafruit-ampy

# Upload a script as main.py (runs on boot)
ampy --port /dev/ttyUSB0 put weather_standalone.py main.py

# Reboot the device
ampy --port /dev/ttyUSB0 reset
```

---

## Tips & Gotchas

1. **Always call `pk.render()`** - Changes don't appear until you render
2. **Call `pk.check_controls()` before reading inputs** - Updates the state
3. **Button/joystick states are properties, not methods** - Use `pk.is_pressing_a` not `pk.is_pressing_a()`
4. **Dial returns 0-4095** - It's a 12-bit ADC
5. **Memory is limited** - ~70KB free, avoid large data structures
6. **Colors are (R, G, B) tuples** - Each value 0-255

---

## Resources

- [Pixel32 GitHub](https://github.com/murilopolese/pixel32)
- [MicroPython Docs](https://docs.micropython.org/en/latest/)
- [ESP32 MicroPython](https://docs.micropython.org/en/latest/esp32/quickref.html)
- [Original Instructables Guide](https://www.instructables.com/Flashing-MicroPython-on-Kano-Pixel-Kit/)
