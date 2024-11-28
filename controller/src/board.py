import json
import struct
import socket
import logging
import numpy as np

from surface_base import AbstractSurface
import color
from client import TcpClient

log = logging.getLogger(__name__)

DEFAULT_PORT = 50_000

BOARD_8_32 = (8, 32)
BOARD_16_32 = (16, 32)


class Board(AbstractSurface):
    def __init__(self, name, board_type, position_tuple, ip, port=DEFAULT_PORT):
        self.board_type = tuple(board_type)
        if not self.board_type in self._supported_boards():
            raise Exception("Unsupported board size: ", board_type)

        super().__init__(name, board_type, position_tuple)

        self.ip = ip
        self.port = port

        self.client = TcpClient(self.ip, self.port)

    def write_through_client(self):
        self.client.send(self.pixels.tolist())

    def write(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.ip, self.port))

                message = self._create_message(self.pixels.tolist())

                s.sendall(message)
        except ConnectionRefusedError as e:
            log.error(
                f"Could not connect to board {self.name} at {self.ip}:{self.port}"
            )
        except OSError as e:
            log.error(f"{e}: {self.name} at {self.ip}:{self.port}")

    def pixel_index(self, x, y):
        if x < 0 or x >= self.size.width or y < 0 or y >= self.size.height:
            return None

        if self.board_type == BOARD_8_32:
            return self._pixel_index_8_32(x, y)
        elif self.board_type == BOARD_16_32:
            return self._pixel_index_16_32(x, y)
        else:
            raise Exception("Unsupported board size: ", self.board_type)

    def _drawn_pixel_map(self):
        drawn_pixel_map = {}
        for index, pixel_color in enumerate(self.pixels):
            if not np.array_equal(pixel_color, np.array(color.COLOR_BLACK)):
                drawn_pixel_map[index] = pixel_color.tolist()
        return drawn_pixel_map

    def _pixel_index_16_32(self, x, y):
        if x <= (self.size.width // 2 - 1):
            if y % 2 > 0:
                return (y * 8) + x
            else:
                return (y * 8) + (7 - x)
        else:
            if y % 2 > 0:
                return (self.size.height * 2 - (1 + y)) * 8 + x % 8
            else:
                return (self.size.height * 2 - (1 + y)) * 8 + (
                    (self.size.width // 2 - 1) - x % 8
                )

    def _pixel_index_8_32(self, x, y):
        if y % 2 > 0:
            return y * self.size.width + x
        else:
            return y * self.size.width + (self.size.width - 1 - x)

    def _create_message(self, payload):
        flat_payload = [val for pixel in payload for val in pixel]

        message_header = struct.pack(">H", len(flat_payload))

        pixel_format = "B" * len(flat_payload)
        message_content = struct.pack(pixel_format, *flat_payload)

        return message_header + message_content

    def _supported_boards(self):
        return [
            BOARD_8_32,
            BOARD_16_32,
        ]

    def __repr__(self):
        return f"Board(name='{self.name}', board_type={self.board_type}, position={self.position}, ip='{self.ip}', port={self.port})"
