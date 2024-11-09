import pygame
import logging

from surface_base import AbstractSurface

log = logging.getLogger(__name__)

PIXEL_SIZE = 20


class Window(AbstractSurface):
    def __init__(self, name, dimension, position_tuple):
        super().__init__(name, dimension, position_tuple)

        self.screen = pygame.Surface(
            (self.width * PIXEL_SIZE, self.height * PIXEL_SIZE)
        )

        log.info("Initialized Window: width=%s, height=%s", self.width, self.height)

    def write(self):
        for y in range(self.height):
            for x in range(self.width):
                index = self.pixel_index(x, y)
                color = self.pixels[index]
                pygame.draw.rect(
                    self.screen,
                    color,
                    (
                        x * PIXEL_SIZE,
                        y * PIXEL_SIZE,
                        PIXEL_SIZE,
                        PIXEL_SIZE,
                    ),
                )

    def __repr__(self):
        return f"Window(width='{self.width}', height='{self.height}')"
