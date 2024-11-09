from abc import ABC, abstractmethod

import logging
import color

log = logging.getLogger(__name__)


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Position(x={self.x}, y={self.y})"


class AbstractSurface(ABC):
    def __init__(self, name, dimension, position_tuple):
        self.name = name
        self.width = dimension[0]
        self.height = dimension[1]
        self.position = Position(position_tuple[0], position_tuple[1])
        self.num_pixels = self.width * self.height

        self.pixels = [color.COLOR_BLACK] * self.width * self.height

    @abstractmethod
    def write(self):
        pass

    def fill(self, pixel_color):
        self.pixels = [pixel_color] * self.num_pixels

    def draw_pixel(self, x, y, pixel_color):
        index = self.pixel_index(x, y)
        if 0 <= index < self.num_pixels:
            self.pixels[index] = pixel_color

    def draw_circle(self, x, y, radius, pixel_color):
        for i in range(-radius, radius + 1):
            for j in range(-radius, radius + 1):
                if i * i + j * j <= radius * radius:
                    self.draw_pixel(x + i, y + j, pixel_color)

    def pixel_index(self, x, y):
        return y * self.width + x
