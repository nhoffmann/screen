import time, random
import threading
from send_to_board import send_to_board
import board

IP_1 = '192.168.1.224'
IP_2 = '192.168.1.93'
PORT = 50_000  

board_1 = board.Board(board.BOARD_8_32, IP_2)
# board_2 = board.Board(board.BOARD_8_32, IP_2)

WAIT = 0.1

# Light up one pixel after the other starting top left and moving right and down the rows
for y in range(board_1.height):
    for x in range(board_1.width):
        board_1.pixel_array[board_1.pixel_index(x, y)] = board.COLOR_BLUE
        time.sleep(WAIT)
        board_1.send()

# while True:
    # # Bar moving down the led matrix
    # for y in range(HEIGHT):
    #     time.sleep(WAIT)
    #     for x in range(WIDTH):
    #         arr[map_idx(x, y)] = (r, g, b)
    #         if y - 1 >= 0: 
    #             arr[map_idx(x, y -1)] = OFF	
    #     send_to_board(BOARD_1, arr)    

    # # Strobe light
    # for i in range(NUM_PIXELS):		
    #     arr[i] = WHITE
    # send_to_board(BOARD_1, arr)
    # time.sleep(WAIT)
    # for i in range(NUM_PIXELS):		
    #     arr[i] = OFF
    # send_to_board(BOARD_1, arr)
    # time.sleep(WAIT)

    # # random blinky lights
    # for y in range(board_1.height):		
    #     for x in range(board_1.width):
    #         board_1.pixel_array[board_1.pixel_index(x, y)] = board.COLOR_MEDIUM_WHITE if random.random() < 0.1 else board.COLOR_BLACK
    # board_1.send()
    # time.sleep(WAIT)

    ## Switch all off
    # for i in range(NUM_PIXELS):		
    #  	arr[i] = OFF

    # # Switch all on
    # for i in range(NUM_PIXELS):		
    #     arr[i] = MEDIUM_WHITE
    # send_to_board(BOARD_1, arr)
