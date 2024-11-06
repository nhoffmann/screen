from machine import Pin
from neopixel import NeoPixel
from time import sleep
import re 

OFF = (0, 0, 0)
WHITE_255 = (255, 255, 255)
WHITE_64 = (64, 64, 64)
White_1 = (1, 1, 1)

class LedMatrix:
    def __init__(self, width=8, height=32, pin=2):
        self.width = width 
        self.height = height 
        self._num_pixels = self.width * self.height
        self._pin = pin
        self._np = None

        self._create_led_matrix()
        print("LED matrix ready.")


    def _create_led_matrix(self):
        pin = Pin(2, Pin.OUT) 
        self._np = NeoPixel(pin, self._num_pixels, bpp=3)

    def _write_all(self, color_tuple):
        for i in range(self._num_pixels):		
            self._np[i] = color_tuple
        self._np.write()
        
    def write(self, color_array):
        for i in range(len(color_array)):
            self._np[i] = color_array[i]
        self._np.write()

    def write_from_hex(self, hex_string):
        step = 6 
        hex_arr = [hex_string[i:i+step] for i in range(0, len(hex_string), step)] 
        for i in range(len(hex_arr)):
            self._np[i] = self._hex2rgb(hex_arr[i])
        self._np.write()

    def blackout(self):
        self._write_all(OFF)

    def whiteout(self):
        self._write_all(WHITE_64)

    def test(self):
        for k in range(3):
            self.whiteout()
            sleep(0.2)
            self.blackout()

    def _hex2rgb(self, hexcode):
        return tuple(int(hexcode[i:i+2], 16) for i in (0, 2, 4))
