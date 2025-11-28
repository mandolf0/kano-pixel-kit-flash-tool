import os
import sys
import esptool
from PyQt5.QtCore import QThread, pyqtSignal
from .logger import setupLogger
import logging

setupLogger()

class DeviceFlasher(QThread):
    """
    Used to flash the Pixel Kit in a non-blocking manner.
    """
    # Emitted when flashing the Pixel Kit fails for any reason.
    on_flash_fail = pyqtSignal(str)
    # Emitted when flasher outputs data
    on_data = pyqtSignal(str)
    # Emitted when flasher outputs progress status
    on_progress = pyqtSignal(str)
    # Serial port to flash
    port = None
    # What kind of firmware to flash
    firmware_type = "micropython"

    def __init__(self, port):
        QThread.__init__(self)
        self.port = port

    def run(self):
        """
        Flash the device.
        """
        msg = "Unknown firmware type"
        logging.error(msg)
        self.on_flash_fail.emit(msg)

    def get_addr_filename(self, values):
        """
        Given a list of tuples containing the memory address and file addresses
        to write at that address, return another list of tuples containing
        the address and a file (stream) object.
        """
        if not isinstance(values, list):
            self.on_flash_fail.emit('Values must be a list.')
            return
        if any(not isinstance(value, tuple) for value in values):
            self.on_flash_fail.emit('Values items must be tuples.')
            return
        addr_filename = []
        try:
            for value in values:
                addr = int(value[0], 0)
                file = open(value[1], 'rb')
                addr_filename.append((addr, file))
            return addr_filename
        except Exception as ex:
            logging.error(ex)
            self.on_flash_fail.emit('Could not open file.')

    def flash(self, addr_filename=[]):
        """
        Flash firmware to the board using esptool (5.x API)
        """
        self.on_data.emit("Preparing to flash memory. This can take a while.")
        esp = None
        try:
            # Detect and connect to the ESP32 chip (esptool 5.x API)
            esp = esptool.detect_chip(port=self.port, baud=115200)
            # Load the stub flasher into RAM (required for erase/write operations)
            esp = esptool.run_stub(esp)
            # Change baudrate to flash the board faster
            esp.change_baud(921600)
            # Erase the current flash memory first
            self.on_data.emit('Erasing flash memory.')
            esptool.erase_flash(esp)
            self.on_data.emit('Writing on flash memory.')
            # Intercept what esptool prints out
            old_stdout = sys.stdout
            sys.stdout = WritingProgressStdout(self.on_progress)
            # Write to flash memory (esptool 5.x API uses addr_data directly)
            esptool.write_flash(
                esp,
                addr_filename,
                flash_freq="40m",
                flash_mode="dio",
                flash_size="detect"
            )
            # Restore old `sys.stdout`
            sys.stdout = old_stdout
            # Reset the board
            esp.hard_reset()
        except Exception as ex:
            logging.error(ex)
            self.on_flash_fail.emit("Could not write to flash memory.")
        finally:
            if esp:
                try:
                    esp._port.close()
                except:
                    pass

class WritingProgressStdout:
    """
    Replacement for `sys.stdout` that parses the esptool writing progress to
    emit only the progress percentage
    """
    def __init__(self, on_data):
        self.on_data = on_data
        self.status = ''

    def write(self, string):
        is_writing = string.find('Writing at')
        if is_writing != -1:
            status = string[string.find('(')+1:string.find(')')]
            if status != self.status:
                self.on_data.emit(status)
            if status == '100 %':
                self.on_data.emit('Wait for it!')
            self.status = status

    def flush(self):
        None
