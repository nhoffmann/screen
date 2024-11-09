from time import sleep
import logging
import random

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

from controller import Controller
from adapter_board import BoardAdapter
from adapter_window import AdapterWindow
import color

board_adapter = BoardAdapter("config.toml")
window_adapter = AdapterWindow("config.toml")

controller = Controller(window_adapter.width, window_adapter.height)
controller.add_adapter(board_adapter)
controller.add_adapter(window_adapter)

WAIT = 0.04

try:
    while True:
        # # Light up one pixel after the other starting top left and moving right and down the rows
        # for y in range(controller.height):
        #     for x in range(controller.width):
        #         controller.draw(x, y, color.COLOR_BLUE)
        #         controller.draw(x - 1, y, color.COLOR_BLACK)
        #         controller.write()
        #         sleep(WAIT)

        ## Strobe
        # controller.fill(color.COLOR_MEDIUM_WHITE)
        # controller.write()
        # sleep(WAIT)
        # controller.fill(color.COLOR_RED)
        # controller.write()
        # sleep(WAIT)

        # random blinky lights
        for y in range(controller.height):
            for x in range(controller.width):
                controller.draw_pixel(
                    x,
                    y,
                    (
                        color.COLOR_BRIGHT_WHITE
                        if random.random() < 0.1
                        else color.COLOR_BLACK
                    ),
                )
        controller.write()
        sleep(WAIT)

except KeyboardInterrupt:
    controller.clear()
    controller.write()
    print("Exiting...")
