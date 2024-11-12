import time
import esper
import random

from dataclasses import dataclass as component
from controller import Controller
from adapter_board import BoardAdapter
from adapter_window import AdapterWindow
import color

import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

log = logging.getLogger(__name__)


FPS = 25


@component
class Velocity:
    x: float = 0.0
    y: float = 0.0


@component
class Position:
    x: int = 0
    y: int = 0


@component
class Size:
    width: int = 0
    height: int = 0


@component
class Rectangle:
    pass


@component
class Growing:
    growth_increment: int = 0


@component
class Color:
    value: tuple = (0, 0, 0)


@component
class Char:
    letter: str
    type: str = "5x7"
    size: int = 2


class MovementProcessor(esper.Processor):
    def __init__(self, size):
        super().__init__()
        self.size = size

    def process(self):
        for ent, (velocity, position) in esper.get_components(Velocity, Position):
            position.x += velocity.x
            position.y += velocity.y

            # # Bounce off
            # if position.x < 0 or position.x > self.size.width:
            #     velocity.x *= -1
            # if position.y < 0 or position.y > self.size.height:
            #     velocity.y *= -1


class RenderRectanglesProcessor(esper.Processor):
    def __init__(self, controller):
        self.controller = controller

    def process(self):
        for ent, (rectangle, position, size, color, growing) in esper.get_components(
            Rectangle, Position, Size, Color, Growing
        ):
            log.debug(f"Drawing entity {ent}")
            self.controller.draw_rectangle(
                position.x,
                position.y,
                size.width,
                size.height,
                color.value,
            )


class RenderCharsProcessor(esper.Processor):
    def __init__(self, controller):
        self.controller = controller

    def process(self):
        for ent, (char, position, color) in esper.get_components(Char, Position, Color):
            if position.x + 7 < 0 or position.x > self.controller.width:
                continue

            self.controller.draw_char(
                position.x * char.size,
                position.y * char.size,
                char.letter,
                color.value,
                font_type=char.type,
                pixel_size=char.size,
            )


class CreateRectangleProcessor(esper.Processor):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def process(self):
        if random.randint(0, 100) < 30:
            create_rectangle(
                random.randint(0, self.width),
                random.randint(0, self.height),
                1,
                1,
                0,
                0,
                (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
                ),
                1,
            )


class GrowthProcessor(esper.Processor):
    def process(self):
        for ent, (growing, size) in esper.get_components(Growing, Size):
            if growing.growth_increment == 0:
                return

            growing.growth_increment += 1

            size.width += growing.growth_increment
            size.height += growing.growth_increment

            if size.width > 20:
                log.debug("Deleting entity %s", ent)
                esper.delete_entity(ent, True)


def create_rectangle(x, y, width, height, velocity_x, velocity_y, color, growth=0):
    rect = esper.create_entity()
    esper.add_component(rect, Rectangle())
    esper.add_component(rect, Position(x, y))
    esper.add_component(rect, Size(width, height))
    esper.add_component(rect, Color(color))
    esper.add_component(rect, Velocity(velocity_x, velocity_y))
    esper.add_component(rect, Growing(growth))

    return rect


def racing_rectangles():
    create_rectangle(0, 5, 3, 3, 3, 0, color.COLOR_RED)
    create_rectangle(0, 10, 3, 3, 2, 0, color.COLOR_RED)
    create_rectangle(0, 15, 3, 3, 1, 0, color.COLOR_RED)
    create_rectangle(5, 20, 3, 3, 3, 0, color.COLOR_RED)
    create_rectangle(10, 25, 3, 3, 1, 0, color.COLOR_RED)
    create_rectangle(13, 30, 3, 3, 2, 0, color.COLOR_RED)


def spiral_rectangles(height):
    for i in range(0, height, 1):
        create_rectangle(i, int(i * 2), 2, 2, 1, 0, color.opacity(color.COLOR_BLUE, 1))


def exploding_rectangles(width, height):
    for i in range(1):
        grow = random.randint(1, 3)
        create_rectangle(
            random.randint(0, width),
            random.randint(0, height),
            2,
            2,
            0,
            0,
            color.COLOR_BLUE,
            1,
        )


def random_rectangle(width, height):
    create_rectangle(
        random.randint(0, width),
        random.randint(0, height),
        2,
        2,
        0,
        0,
        color.COLOR_BLUE,
        growth=1,
    )


def create_char(letter, x, y, color):
    char = esper.create_entity()
    esper.add_component(char, Char(letter=letter.upper()))
    esper.add_component(char, Position(x, y))
    esper.add_component(char, Color(color))
    esper.add_component(char, Velocity(-1, 0))


def marlena_frank(width):
    create_char("M", width + 0, 5, color.COLOR_BLUE)
    create_char("A", width + 6, 5, color.COLOR_BLUE)
    create_char("L", width + 18, 5, color.COLOR_BLUE)
    create_char("R", width + 12, 5, color.COLOR_BLUE)
    create_char("E", width + 24, 5, color.COLOR_BLUE)
    create_char("N", width + 30, 5, color.COLOR_BLUE)
    create_char("A", width + 36, 5, color.COLOR_BLUE)
    create_char("F", width + 42, 5, color.COLOR_BLUE)
    create_char("R", width + 48, 5, color.COLOR_BLUE)
    create_char("A", width + 54, 5, color.COLOR_BLUE)
    create_char("N", width + 60, 5, color.COLOR_BLUE)
    create_char("K", width + 66, 5, color.COLOR_BLUE)


def einseinseins(width):
    create_char("E", width + 0, 5, color.COLOR_BLUE)
    create_char("I", width + 6, 5, color.COLOR_BLUE)
    create_char("N", width + 12, 5, color.COLOR_BLUE)
    create_char("S", width + 18, 5, color.COLOR_BLUE)
    create_char("E", width + 24, 5, color.COLOR_BLUE)
    create_char("I", width + 30, 5, color.COLOR_BLUE)
    create_char("N", width + 36, 5, color.COLOR_BLUE)
    create_char("S", width + 42, 5, color.COLOR_BLUE)
    create_char("E", width + 48, 5, color.COLOR_BLUE)
    create_char("I", width + 54, 5, color.COLOR_BLUE)
    create_char("N", width + 60, 5, color.COLOR_BLUE)
    create_char("S", width + 66, 5, color.COLOR_BLUE)


def main():
    board_adapter = BoardAdapter("config.toml")
    window_adapter = AdapterWindow("config.toml")

    controller = Controller(window_adapter.width, window_adapter.height)
    controller.add_adapter(board_adapter)
    controller.add_adapter(window_adapter)

    movement_processor = MovementProcessor(controller)
    render_rectangles_processor = RenderRectanglesProcessor(controller)
    create_rectangle_processor = CreateRectangleProcessor(
        controller.width, controller.height
    )
    render_chars_processor = RenderCharsProcessor(controller)
    growth_processor = GrowthProcessor()

    # spiral_rectangles(controller.height)
    # exploding_rectangles(controller.width, controller.height)
    einseinseins(controller.width)

    try:
        while True:
            controller.clear()
            movement_processor.process()
            render_rectangles_processor.process()
            # create_rectangle_processor.process()
            render_chars_processor.process()
            growth_processor.process()

            position_xs = []
            for ent, (position, velocity) in esper.get_components(Position, Velocity):
                position_xs.append(position.x)

            if len(position_xs) and max(position_xs) < 0:
                einseinseins(controller.width)

            controller.write()
            time.sleep(1 / FPS)
    except KeyboardInterrupt:
        controller.clear()
        controller.write()
        return


if __name__ == "__main__":
    main()
