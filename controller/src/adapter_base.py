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

    def draw_circle(self, x, y, radius, pixel_color):
        """TODO needs anti aliasing"""
        for i in range(-radius, radius + 1):
            for j in range(-radius, radius + 1):
                if i * i + j * j <= radius * radius:
                    self.draw_pixel(x + i, y + j, pixel_color)

    def draw_rectangle(self, x, y, width, height, pixel_color):
        for i in range(width):
            for j in range(height):
                self.draw_pixel(x + i, y + j, pixel_color)

    def draw_line(self, x1, y1, x2, y2, pixel_color):
        """Bresenham's line algorithm"""
        """Should probably be implemented using Wus line algorithm"""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            self.draw_pixel(x1, y1, pixel_color)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

    def fill(self, pixel_color):
        for surface in self.surfaces.values():
            surface.fill(pixel_color)

    @abstractmethod
    def write(self):
        pass

    def _surface_and_position_for_pixel(self, x, y):
        index = self._pixel_index(x, y)
        if index is None:
            return None, None
        if index >= len(self._pixel_to_surface):
            return None, None

        pixel_to_surface = self._pixel_to_surface[index]
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
            right_most_pixel.append(surface.position.x + surface.size.width)
            bottom_most_pixel.append(surface.position.y + surface.size.height)

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
            surface.position.x <= x < surface.position.x + surface.size.width
            and surface.position.y <= y < surface.position.y + surface.size.height
        )

    def _pixel_index(self, x, y):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return None
        return y * self.width + x
