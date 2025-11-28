"""
Weather & Time Display for Kano Pixel Kit - Standalone MicroPython version
Runs entirely on the ESP32, fetches weather via WiFi.
Upload this as main.py to the device.
"""
import network
import urequests
import time
import PixelKit as pk

# --- Configuration ---
WIFI_SSID = 'YOUR_SSID_HERE'
WIFI_PASSWORD = 'YOUR_PASSWORD_HERE'
ZIP_CODE = '00000'
DISPLAY_INTERVAL = 5  # seconds

# 3x5 font for digits 0-9, degree, minus, plus
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
    '°': ['11', '11', '00', '00', '00'],
    '-': ['000', '000', '111', '000', '000'],
    '+': ['000', '010', '111', '010', '000'],
    ' ': ['0', '0', '0', '0', '0'],
}


def connect_wifi():
    """Connect to WiFi network"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        timeout = 20
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
    if wlan.isconnected():
        print('WiFi connected:', wlan.ifconfig())
        return True
    else:
        print('WiFi connection failed')
        return False


def sync_time():
    """Sync RTC with NTP server and adjust for CST (UTC-6)"""
    import ntptime
    try:
        ntptime.settime()
        print('Time synced (UTC)')
    except Exception as e:
        print('NTP sync failed:', e)


def get_temperature():
    """Fetch temperature from wttr.in"""
    try:
        url = 'https://wttr.in/{}?format=%t&u'.format(ZIP_CODE)
        response = urequests.get(url)
        temp = response.text.strip()
        response.close()
        # Returns like "+29°F" or "-2°F"
        return temp.replace('°F', '°')
    except Exception as e:
        print('Weather error:', e)
        return None


def get_time_12h():
    """Get current time in 12hr format from RTC (CST = UTC-6)"""
    t = time.localtime()
    hour = (t[3] - 6) % 24  # UTC to CST
    minute = t[4]
    # Convert to 12hr
    if hour == 0:
        hour = 12
    elif hour > 12:
        hour -= 12
    return '{:02d}'.format(hour), '{:02d}'.format(minute)


def render_text_at(text, x_start, color):
    """Render text at given x offset"""
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
                        pk.set_pixel(x, y, color)
        x_offset += len(glyph[0]) + 1


def render_text(text, color):
    """Render text centered on display"""
    pk.clear()
    render_text_at(text, 0, color)
    pk.render()


def show_error():
    """Flash red to indicate error"""
    pk.set_background((20, 0, 0))
    pk.render()
    time.sleep(0.5)
    pk.clear()
    pk.render()


def main():
    # Show startup
    pk.set_background((0, 0, 10))
    pk.render()

    if not connect_wifi():
        show_error()
        return

    sync_time()

    pk.clear()
    pk.render()

    show_temp = True
    last_temp = None

    while True:
        try:
            if show_temp:
                temp = get_temperature()
                if temp:
                    last_temp = temp
                    print('Temp:', temp)
                    render_text(temp, (13, 17, 23))
                elif last_temp:
                    render_text(last_temp, (13, 17, 23))
                else:
                    show_error()
            else:
                hours, mins = get_time_12h()
                print('Time:', hours, mins)
                pk.clear()
                render_text_at(hours, 0, (23, 17, 3))
                render_text_at(mins, 9, (10, 15, 23))
                pk.render()

            show_temp = not show_temp
            time.sleep(DISPLAY_INTERVAL)

        except Exception as e:
            print('Error:', e)
            show_error()
            time.sleep(5)


# Run on import (when used as main.py)
main()
