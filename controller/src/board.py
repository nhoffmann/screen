import json
import struct
import socket
import logging

from surface_base import AbstractSurface

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

    def write(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip, self.port))
            pixel_array_encoded = self._json_encode(self.pixels)
            message = self._create_message(pixel_array_encoded)
            s.sendall(message)

    def pixel_index(self, x, y):
        if self.board_type == BOARD_8_32:
            return self._pixel_index_8_32(x, y)
        elif self.board_type == BOARD_16_32:
            return self._pixel_index_16_32(x, y)

    def _pixel_index_16_32(self, x, y):
        if x <= (int(self.width / 2) - 1):
            if y % 2 > 0:
                return (y * 8) + x
            else:
                return (y * 8) + (7 - x)
        else:
            if y % 2 > 0:
                return (self.height * 2 - (1 + y)) * 8 + x % 8
            else:
                return (self.height * 2 - (1 + y)) * 8 + (
                    (int(self.width / 2) - 1) - x % 8
                )

    def _pixel_index_8_32(self, x, y):
        if y % 2 > 0:
            return y * self.width + x
        else:
            return y * self.width + (self.width - 1 - x)

    def _json_encode(self, obj):
        return json.dumps(obj).encode()

    def _create_message(self, content_bytes):
        message_header = struct.pack(">H", len(content_bytes))
        return message_header + content_bytes

    def _supported_boards(self):
        return [
            BOARD_8_32,
            BOARD_16_32,
        ]

    def __repr__(self):
        return f"Board(name='{self.name}', board_type={self.board_type}, position={self.position}, ip='{self.ip}', port={self.port})"

    ### Experimental

    def send_as_hex(self):
        """Experimental: Converting the pixel tupel array into a hextring and sending
        that over the wire. Unfortunately, micropython can not decode the data
        fast enough.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip, self.port))
            pixel_array_encoded = self.hex_encode(self.pixel_array)
            message = self.create_message(pixel_array_encoded)
            print(message)
            s.sendall(message)

    def hex_encode(self, arr):
        hexarr = ""
        for rgb_tuple in arr:
            hexarr += self._rgb2hex(rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])
        return hexarr.encode()

    def _rgb2hex(self, r, g, b):
        return "{:02x}{:02x}{:02x}".format(r, g, b)

    def _hex2rgb(self, hexcode):
        return tuple(int(hexcode[i : i + 2], 16) for i in (0, 2, 4))
