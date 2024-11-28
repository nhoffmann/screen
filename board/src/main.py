from led_matrix import LedMatrix
from server import TcpServer
import gc

print("GC threhshold to begin with: ", gc.threshold())
gc.enable()

# TODO make this configurable from the outside, so we don't have to flash the
# board every time we want to change the size
WIDTH = 8
HEIGHT = 32

led_matrix = LedMatrix(WIDTH, HEIGHT)
led_matrix.test()

server = TcpServer()
gc.collect()
gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

print("GC threhshold: ", gc.threshold())

server.handle_requests(led_matrix.write_array)
