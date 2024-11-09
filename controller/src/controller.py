import logging

import color

log = logging.getLogger(__name__)


class Controller:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.adapters = []

        log.info("Initialized Controller: width=%s, height=%s", width, height)

    def add_adapter(self, adapter):
        self.adapters.append(adapter)
        log.info("Added adapter: %s", adapter)

    def draw_pixel(self, x, y, pixel_color):
        for adapter in self.adapters:
            adapter.draw_pixel(x, y, pixel_color)

    def fill(self, pixel_color):
        for adapter in self.adapters:
            adapter.fill(pixel_color)

    def write(self):
        for adapter in self.adapters:
            adapter.write()

    def clear(self):
        self.fill(color.COLOR_BLACK)

    def __repr__(self):
        return f"Controller(width='{self.width}', height='{self.height}', adapters='{self.adapters}')"


# TODOS
# DONE calculate full controller size by adding all the boards
# DONE draw to "screen" and send it to the boards
# create a run loop that executes animations on all available boards
# somehow modify the run loop so it can read external "animation scripts" and inject them into the run loop
# Write animations
# ...
