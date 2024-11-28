from board import Board
import logging
import threading
from adapter_base import AdapterBase

log = logging.getLogger(__name__)


class BoardAdapter(AdapterBase):
    def __init__(self, config_file):
        super().__init__(config_file)

        log.info(
            "Initialized BoardAdapter: Boards(%s)",
            ", ".join([board for board in self.surfaces.keys()]),
        )

    def write(self):
        log.debug("writing to boards")

        for board in self.surfaces.values():
            thread = threading.Thread(target=board.write)
            thread.start()

    def add_surface(self, name, dimension, position, ip_address):
        board = Board(name, dimension, position, ip_address)
        self.surfaces[name] = board

    def __repr__(self):
        return f"BoardAdapter(width='{self.width}', height='{self.height}', boards='{self.surfaces}')"
