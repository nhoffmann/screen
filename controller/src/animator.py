import time
import esper
import random

from dataclasses import dataclass as component
from controller import Controller
from adapter_board import BoardAdapter
from adapter_window import AdapterWindow
import color


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


class MovementProcessor(esper.Processor):
    def __init__(self, size):
        super().__init__()
        self.size = size

    def process(self):
        for ent, (velocity, position) in esper.get_components(Velocity, Position):
            position.x += velocity.x
            position.y += velocity.y

            if position.x < 0 or position.x > self.size.width:
                velocity.x *= -1
            if position.y < 0 or position.y > self.size.height:
                velocity.y *= -1


class RenderRectanglesProcessor(esper.Processor):
    def __init__(self, controller):
        self.controller = controller

    def process(self):
        self.controller.clear()
        for ent, (rectangle, position, size, color) in esper.get_components(
            Rectangle, Position, Size, Color
        ):
            self.controller.draw_rectangle(
                position.x, position.y, size.width, size.height, color.value
            )
        self.controller.write()


class GrowthProcessor(esper.Processor):
    def process(self):
        for ent, (growing) in esper.get_components(Growing):
            if growing.growth_increment > 0:
                growing.growth_increment += 1

                if growing.growth_increment > 10:
                    esper.remove_


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
        create_rectangle(i, int(i * 2), 2, 2, 1, 0, color.COLOR_BLUE)


def exploding_rectangles(width, height):
    for i in range(width):
        grow = random.randint(1, 3)
        create_rectangle(
            random.randint(0, width),
            random.randint(0, height),
            2 + grow,
            2 + grow,
            0,
            0,
            color.COLOR_BLUE,
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


def main():
    board_adapter = BoardAdapter("config.toml")
    window_adapter = AdapterWindow("config.toml")

    controller = Controller(window_adapter.width, window_adapter.height)
    controller.add_adapter(board_adapter)
    controller.add_adapter(window_adapter)

    movement_processor = MovementProcessor(controller)
    render_rectangles_processor = RenderRectanglesProcessor(controller)

    spiral_rectangles(controller.height)
    # exploding_rectangles(controller.width, controller.height)

    try:
        while True:
            movement_processor.process()
            render_rectangles_processor.process()
            time.sleep(1 / FPS)
    except KeyboardInterrupt:
        controller.clear()
        controller.write()
        return


if __name__ == "__main__":
    main()
