from led_matrix import LedMatrix
from server import TcpServer

WIDTH = 8
HEIGHT = 32

led_matrix = LedMatrix(WIDTH, HEIGHT)
led_matrix.test()

server = TcpServer()
server.handle_requests(led_matrix.write)
