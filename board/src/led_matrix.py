from machine import Pin
from neopixel import NeoPixel
import time

_OFF = const((0, 0, 0))
_WHITE_64 = const((64, 64, 64))


class LedMatrix:
    def __init__(self, width=8, height=32, pin=2):
        self.width = width
        self.height = height
        self._num_pixels = self.width * self.height
        self._pin = pin
        self._np = None

        pin = Pin(4, Pin.OUT)
        self._np = NeoPixel(pin, self._num_pixels, bpp=3)
        print("LED matrix ready.")

    def _write_all(self, color_tuple):
        self.fill(color_tuple)
        self._np.write()

    def fill(self, color_tuple):
        self._np.fill(color_tuple)

    def clear(self):
        self._np.fill(_OFF)

    def write_array(self, color_array):
        # start = time.ticks_us()
        for i in range(len(color_array)):
            self._np[i] = color_array[i]
        self._np.write()
        # print(f"write_array takes: {time.ticks_us() - start} us")

    def blackout(self):
        self._write_all(_OFF)

    def whiteout(self):
        self._write_all(_WHITE_64)

    def test(self):
        for _ in range(3):
            self.whiteout()
            time.sleep(0.2)
            self.blackout()
