from time import sleep
import logging
import random
import cv2

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

from controller import Controller
from adapter_board import BoardAdapter
from adapter_window import AdapterWindow
import color

log = logging.getLogger(__name__)

board_adapter = BoardAdapter("config.toml")
window_adapter = AdapterWindow("config.toml")

controller = Controller(window_adapter.width, window_adapter.height)
controller.add_adapter(board_adapter)
controller.add_adapter(window_adapter)

WAIT = 1 / 25

circles = []


def bar_moving_down_the_led_matrix():
    for y in range(controller.height):
        sleep(WAIT)
        for x in range(controller.width):
            controller.draw_pixel(x, y, color.COLOR_BLUE)
            if y - 1 >= 0:
                controller.draw_pixel(x, y - 1, color.COLOR_BLACK)
        controller.write()


def strobe(pixel_color_1, pixel_color_2):
    controller.fill(pixel_color_1)
    controller.write()
    sleep(WAIT)
    controller.fill(pixel_color_2)
    controller.write()
    sleep(WAIT)


def light_up_one_pixel_at_a_time(pixel_color):
    for y in range(controller.height):
        for x in range(controller.width):
            controller.draw_pixel(x, y, pixel_color)
            controller.draw_pixel(x - 1, y, color.COLOR_BLACK)
            controller.write()
            sleep(WAIT)


def random_blinky_lights(pixel_color):
    for y in range(controller.height):
        for x in range(controller.width):
            controller.draw_pixel(
                x,
                y,
                (pixel_color if random.random() < 0.1 else color.COLOR_BLACK),
            )
    controller.write()
    sleep(WAIT)


def exploding_circles(circle_color):
    if random.random() < 0.1:
        origin_x = random.randint(0, controller.width - 1)
        origin_y = random.randint(0, controller.height - 1)

        radius = 1
        log.info("Adding circle at x=%s, y=%s, radius=%s", origin_x, origin_y, radius)

        circles.append([origin_x, origin_y, radius])

    controller.clear()
    log.info("Drawing circles")
    for circle in circles:
        log.info(
            "Drawing circle at x=%s, y=%s, radius=%s",
            circle[0],
            circle[1],
            circle[2],
        )
        controller.draw_circle(origin_x, origin_y, radius, color.COLOR_RED)

    log.info("Growing circles")
    for circle in circles:
        circle[2] += 1
        log.info(
            "Growing circle at x=%s, y=%s, radius=%s",
            circle[0],
            circle[1],
            circle[2],
        )

    log.info("Removing circles that are too big")
    circles = [circle for circle in circles if circle[2] < 20]

    controller.write()

    sleep(WAIT)


def draw_video(video_path):
    cap = cv2.VideoCapture(video_path)

    okay, frame = cap.read()
    frame_number = 0
    print(f"# Video appears to be {len(frame[0])} x {len(frame)}")

    while okay:
        for y, row in enumerate(frame):
            for x, pixel in enumerate(row):
                if x >= controller.width:
                    break
                controller.draw_pixel(
                    x, y, (int(pixel[0]), int(pixel[1]), int(pixel[2]))
                )
            if y >= controller.height:
                break

        controller.write()
        log.info("Processed frame: %s", frame_number)
        frame_number += 1

        sleep(WAIT)
        okay, frame = cap.read()


try:
    while True:
        # light_up_one_pixel_at_a_time(color.COLOR_BLUE)

        # bar_moving_down_the_led_matrix()

        # strobe(color.COLOR_RED, color.COLOR_BRIGHT_WHITE)

        # random_blinky_lights(color.COLOR_BLUE)

        # exploding_circles(color.COLOR_RED)

        # draw_video("../../assets/bw_lines_smaller_contrast.mp4")
        # draw_video("../../assets/colors_rotated_smaller_contrast.mp4")
        # draw_video("../../assets/hyperspace_rotated_smaller_contrast.mp4")
        # draw_video("../../assets/planes_rotated_smaller_contrast.mp4")
        draw_video("../../assets/spiral_rotated_smaller_contrast.mp4")


except KeyboardInterrupt:
    controller.clear()
    controller.write()
    print("Exiting...")
