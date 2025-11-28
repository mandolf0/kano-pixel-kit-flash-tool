# Pixel Kit Flash Tool

![](https://i.imgur.com/x1J3YPM.png)

This is a very simple tool to flash your Pixel Kit with the [Kano Code](https://kano.me/landing/app/uk) firmware (factory firmware) and [MicroPython](https://micropython.org) (with [pixel32](http://github.com/murilopolese/pixel32)).

## About This Fork

This is an updated version of the original [kano-pixel-kit-flash-tool](https://github.com/murilopolese/kano-pixel-kit-flash-tool) by Murilo Polese. The original project was last updated in November 2018 and no longer works with modern versions of esptool (4.x+).

### What Was Updated

- **deviceflasher.py**: Updated to use esptool 5.x API
  - Changed `esptool.ESPLoader.detect_chip()` to `esptool.detect_chip()`
  - Added `esptool.run_stub()` call (required before flash operations)
  - Updated `erase_flash()` and `write_flash()` function signatures
  - Added proper serial port cleanup
- **app.py**: Fixed thread lifecycle issues
  - Added `closeEvent()` to wait for flash thread before exit
  - Fixed logger initialization (was after `sys.exit()`)
- **requirements.txt**: Updated to use esptool >= 5.0

### What Has NOT Been Updated

- **Build scripts** (`build_linux.sh`, `build_macos.sh`, `build_win.bat`): Untested with current dependencies
- **PyInstaller spec files** (`linux.spec`, `macos.spec`, `windows.spec`): Untested
- **appveyor.yml**: Outdated CI configuration
- **setup.py**: Still references old esptool version (use `pip install -r requirements.txt` instead)
- **Firmware files**: Original 2018 versions (MicroPython 1.9.4, Pixel32 0.2.3, Kano Code 1.0.2)

### Why Not a Fork?

The original repository appears abandoned (last commit 2018). Rather than creating a fork that would never be merged, this is published as a standalone working version for anyone who still has a Kano Pixel Kit.

## Download

For now, run from source (see below). Pre-built binaries are not available.

## Features

- Recognise Pixel Kits connected over USB (refresh ports).
- Flash Kano Code (factory firmware).
- Flash MicroPython and [Pixel32](http://github.com/murilopolese/pixel32) to your board.

## Running From Source

1. Make sure you have Python 3 and pip installed
2. Run `python -m venv venv && source venv/bin/activate`
3. Run `pip install -r requirements.txt`
4. Run `python run.py`

## MicroPython firmware

Pixel32 is a MicroPython application that allows it to be programmed on the browser, offline and with built in documentation. To read more about that, check [Pixel32](http://github.com/murilopolese/pixel32).

## Kano Code firmware

Kano Code firmware is what makes your Pixel Kit able to interact with the [Kano Code App](https://kano.me/landing/app/uk).

## I want more!!

If you are looking at a more complete, flexible yet still friendly way to flash your Pixel Kit I can't recommend [the `nodemcu-pyflasher` project](https://github.com/marcelstoer/nodemcu-pyflasher) enough.

If you are not afraid of command line, perhaps even the [esptool](https://github.com/espressif/esptool) itself?

All you will need to do is to find or build a suitable firmware for ESP32. Here is a list of places you might find it:

- [MicroPython](https://micropython.org/download#esp32)
- [LuaNode](https://github.com/Nicholas3388/LuaNode)
- [Espruino (javascript)](https://www.espruino.com/)
- [BASIC](https://hackaday.com/2016/10/27/basic-interpreter-hidden-in-esp32-silicon/)

## Credits

Original tool by [Murilo Polese](https://github.com/murilopolese). Updated for esptool 5.x compatibility in 2024.
