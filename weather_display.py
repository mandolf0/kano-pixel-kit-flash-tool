#!/usr/bin/env python3
"""
Weather & Time Display for Kano Pixel Kit
Alternates between temperature (60074) and 24hr time every 5 seconds.
"""
import serial
import time
import subprocess
from datetime import datetime

# --- Configuration ---
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200
ZIP_CODE = '60074'
DISPLAY_INTERVAL = 5  # seconds

# 3x5 font for digits 0-9, colon, degree, minus, plus, F
FONT = {
    '0': ['111', '101', '101', '101', '111'],
    '1': ['010', '110', '010', '010', '111'],
    '2': ['111', '001', '111', '100', '111'],
    '3': ['111', '001', '111', '001', '111'],
    '4': ['101', '101', '111', '001', '001'],
    '5': ['111', '100', '111', '001', '111'],
    '6': ['111', '100', '111', '101', '111'],
    '7': ['111', '001', '001', '001', '001'],
    '8': ['111', '101', '111', '101', '111'],
    '9': ['111', '101', '111', '001', '111'],
    ':': ['0', '1', '0', '1', '0'],
    '°': ['11', '11', '00', '00', '00'],
    '-': ['000', '000', '111', '000', '000'],
    '+': ['000', '010', '111', '010', '000'],
    'F': ['111', '100', '111', '100', '100'],
    ' ': ['0', '0', '0', '0', '0'],
}


def get_temperature():
    """Fetch temperature from wttr.in using curl with retries"""
    for attempt in range(3):
        try:
            result = subprocess.run(
                ['curl', '-s', '--max-time', '10', f'https://wttr.in/{ZIP_CODE}?format=%t&u'],
                capture_output=True, text=True, timeout=12
            )
            temp = result.stdout.strip()
            if temp and '°' in temp:
                # Returns like "+29°F" or "-2°F"
                return temp.replace('°F', '°')
        except Exception as e:
            print(f"Weather attempt {attempt+1} failed: {e}")
            time.sleep(2)
    return None


def get_time_12h():
    """Get current time in 12hr format"""
    return datetime.now().strftime('%I:%M')


def render_text_at(text, x_start, color=(20, 20, 20)):
    """Generate pixel commands for text at given x offset (no clear/render)"""
    commands = []
    x_offset = x_start
    for char in text:
        if char not in FONT:
            continue
        glyph = FONT[char]
        for row_idx, row in enumerate(glyph):
            y = row_idx + 2
            for col_idx, pixel in enumerate(row):
                if pixel == '1':
                    x = x_offset + col_idx
                    if 0 <= x < 16 and 0 <= y < 8:
                        commands.append(f'pk.set_pixel({x},{y},{color})')
        x_offset += len(glyph[0]) + 1
    return commands


def render_text(text, color=(20, 20, 20)):
    """Generate MicroPython commands to render text on the matrix"""
    commands = ['pk.clear()']
    commands.extend(render_text_at(text, 0, color))
    commands.append('pk.render()')
    return commands


def send_commands(ser, commands):
    """Send commands to the Pixel Kit"""
    for cmd in commands:
        ser.write((cmd + '\r\n').encode())
        time.sleep(0.02)
    time.sleep(0.1)
    # Clear response buffer
    ser.read(ser.in_waiting)


def main():
    print(f"Connecting to Pixel Kit on {SERIAL_PORT}...")
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(1)

    # Initialize
    ser.write(b'\r\nimport PixelKit as pk\r\n')
    time.sleep(0.5)
    ser.read(ser.in_waiting)

    print("Starting display loop. Ctrl+C to exit.")

    show_temp = True
    last_temp = None

    try:
        while True:
            if show_temp:
                # Fetch and show temperature
                temp = get_temperature()
                if temp:
                    last_temp = temp
                    print(f"Temp: {temp}F")
                    # Dim blue-white for cold
                    commands = render_text(temp, (13, 17, 23))
                    send_commands(ser, commands)
                elif last_temp:
                    commands = render_text(last_temp, (15, 20, 30))
                    send_commands(ser, commands)
            else:
                # Show time - hours and mins in different colors
                current_time = get_time_12h()
                print(f"Time: {current_time}")
                hours, mins = current_time.split(':')
                commands = ['pk.clear()']
                # Hours in amber
                commands.extend(render_text_at(hours, 0, (23, 17, 3)))
                # Minutes in blue
                commands.extend(render_text_at(mins, 9, (10, 15, 23)))
                commands.append('pk.render()')
                send_commands(ser, commands)

            show_temp = not show_temp
            time.sleep(DISPLAY_INTERVAL)

    except KeyboardInterrupt:
        print("\nExiting...")
        send_commands(ser, ['pk.clear()', 'pk.render()'])
        ser.close()


if __name__ == '__main__':
    main()
