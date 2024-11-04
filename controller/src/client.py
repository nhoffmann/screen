import socket, json, time, random

# IP = '127.0.0.1'
IP_1 = '192.168.1.224'
IP_2 = '192.168.1.93'
PORT = 50_000

BOARD_1 = (IP_1, PORT)
BOARD_2 = (IP_2, PORT)

# print("Target IP: ", IP)
# print("Target Port: ", PORT)

# arr = [int(sys.argv[1]), int(sys.argv[2])]

# data_string = json.dumps(arr)
# print(data_string)

## UDP client
# try: 
#     print("Sending data: ", data_string)
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     sock.sendto(data_string.encode(), (IP, PORT))
# except Exception as e:
#     print(e.message, e.args)

WIDTH = 8
HEIGHT = 32

def map_idx(x, y):
	if y % 2 > 0:
		return y * WIDTH + x
	else:
		return y * WIDTH + (WIDTH-1 - x)

OFF = (0, 0, 0)
BRIGHT_WHITE = (255, 255, 255)
MEDIUM_WHITE = (63, 63, 63)
WHITE = (1, 1, 1)

arr = [OFF] * 256
# for i in range(len(arr)):
#     arr[i] = (255, 255, 255)

def send_to_board(arr):
    data_string = json.dumps(arr)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s1:
        s1.connect(BOARD_1)
        s1.sendall(data_string.encode())

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
        s2.connect(BOARD_2)
        s2.sendall(data_string.encode())
	
r, g, b = 0, 127, 255

WAIT = 0.04

while True:
	## Bar moving down the led matrix
    for y in range(HEIGHT):
        time.sleep(0.04)
        for x in range(WIDTH):
            arr[map_idx(x, y)] = (r, g, b)
            arr[map_idx(x, y -1)] = OFF	
        send_to_board(arr)


    # Strobe light
    # for i in range(HEIGHT * WIDTH):		
    #     arr[i] = BRIGHT_WHITE
    # send_to_board(arr)
    # time.sleep(WAIT)
    # for i in range(HEIGHT * WIDTH):		
    #     arr[i] = OFF
    # send_to_board(arr)
    # time.sleep(WAIT)

    # random blinky lights
    # for y in range(HEIGHT):		
    # 	for x in range(WIDTH):
    #         arr[map_idx(x, y)] = MEDIUM_WHITE if random.random() < 0.1 else OFF
    # send_to_board(BOARD_1, arr)
    # send_to_board(BOARD_2, arr)
    # time.sleep(WAIT)

    ## Switch all off
    # for i in range(HEIGHT * WIDTH):		
    #  	arr[i] = OFF
