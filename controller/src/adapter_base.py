from abc import ABC, abstractmethod
import toml
import logging

log = logging.getLogger(__name__)


class AdapterBase(ABC):
    def __init__(self, config_file):
        self.config_file = config_file
        self.surfaces = {}
        self.width = 0
        self.height = 0
        self._pixel_to_surface = {}

        self._load_config()
        self._calculate_size()
        self._calculate_pixel_to_surface()

    def draw_pixel(self, x, y, pixel_color):
        surface, surface_pixel_position = self._surface_and_position_for_pixel(x, y)
        if surface is None:
            return
        log.debug(
            "Drawing pixel at x=%s, y=%s, color=%s to surface=%s",
            x,
            y,
            pixel_color,
            surface.name,
        )
        surface.draw_pixel(
            x=surface_pixel_position[0],
            y=surface_pixel_position[1],
            pixel_color=pixel_color,
        )

    def fill(self, pixel_color):
        for surface in self.surfaces.values():
            surface.fill(pixel_color)

    @abstractmethod
    def write(self):
        pass

    def _surface_and_position_for_pixel(self, x, y):
        pixel_to_surface = self._pixel_to_surface[self._pixel_index(x, y)]
        if pixel_to_surface is None:
            return None, None
        surface_name, pixel_position = pixel_to_surface
        return self.surfaces[surface_name], pixel_position

    def _load_config(self):
        with open(self.config_file, "r") as f:
            config = toml.load(f)

        for surface_name, surface_config in config["surfaces"].items():
            self.add_surface(
                surface_name,
                surface_config["dimension"],
                surface_config["position"],
                surface_config["ip_address"],
            )

    @abstractmethod
    def add_surface(self, name, dimension, position, ip_address):
        pass

    def _calculate_size(self):
        right_most_pixel, bottom_most_pixel = [], []
        for surface in self.surfaces.values():
            right_most_pixel.append(surface.position.x + surface.width)
            bottom_most_pixel.append(surface.position.y + surface.height)

        self.width = max(right_most_pixel)
        self.height = max(bottom_most_pixel)

    def _calculate_pixel_to_surface(self):
        pixel_to_surface = [None] * self.width * self.height

        for y in range(self.height):
            for x in range(self.width):
                pixel_index = self._pixel_index(x, y)
                for surface_name, surface in self.surfaces.items():
                    if self._surface_contains_pixel(surface, x, y):
                        pixel_to_surface[pixel_index] = (
                            surface_name,
                            (x - surface.position.x, y - surface.position.y),
                        )
        self._pixel_to_surface = pixel_to_surface

    def _surface_contains_pixel(self, surface, x, y):
        return (
            surface.position.x <= x < surface.position.x + surface.width
            and surface.position.y <= y < surface.position.y + surface.height
        )

    def _pixel_index(self, x, y):
        return y * self.width + x
