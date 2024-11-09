import toml
import logging
import pygame

import color
from adapter_base import AdapterBase
from window import Window, PIXEL_SIZE

log = logging.getLogger(__name__)


class AdapterWindow(AdapterBase):
    def __init__(self, config_file):
        super().__init__(config_file)

        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.width * PIXEL_SIZE, self.height * PIXEL_SIZE)
        )
        pygame.display.set_caption("Adapter Window")
        pygame.draw.rect(
            self.screen,
            color.COLOR_BRIGHT_WHITE,
            (
                0,
                0,
                self.width * PIXEL_SIZE,
                self.height * PIXEL_SIZE,
            ),
        )

        # self.game_loop()
        # HACK to open the pygame window
        pygame.event.get()

        log.info(
            "Initialized AdapterWindow: Windows(%s)",
            ", ".join([window for window in self.surfaces.keys()]),
        )

    def game_loop(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return

        pygame.quit()

    def write(self):
        for window in self.surfaces.values():
            window.write()
            self.screen.blit(
                window.screen,
                (window.position.x * PIXEL_SIZE, window.position.y * PIXEL_SIZE),
            )
            pygame.display.flip()
            pygame.display.update()

    def add_surface(self, name, dimension, position, _):
        log.info(
            "Adding window: name=%s, dimension=%s, position=%s",
            name,
            dimension,
            position,
        )
        self.surfaces[name] = Window(name, dimension, position)

    def __repr__(self):
        return f"AdapterWindow(windows='{self.surfaces}')"
