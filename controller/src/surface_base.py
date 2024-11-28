from abc import ABC, abstractmethod
from dataclasses import dataclass
import numpy as np

import logging
import color

log = logging.getLogger(__name__)


@dataclass
class Position:
    x: int
    y: int


@dataclass
class Size:
    width: int
    height: int

    def area(self):
        return self.width * self.height


class AbstractSurface(ABC):
    def __init__(self, name, dimension, position):
        self.name = name
        self.size = Size(dimension[0], dimension[1])
        self.position = Position(position[0], position[1])

        self.pixels = np.full((self.size.area(), 3), color.COLOR_BLACK)

    @abstractmethod
    def write(self):
        pass

    def fill(self, pixel_color):
        self.pixels = np.full_like(self.pixels, pixel_color)

    def draw_pixel(self, x, y, pixel_color):
        index = self.pixel_index(x, y)
        if index is not None:
            self.pixels[index] = pixel_color

    def pixel_index(self, x, y):
        if x < 0 or x >= self.size.width or y < 0 or y >= self.size.height:
            # pixel not on the surface
            return None
        return y * self.size.width + x
