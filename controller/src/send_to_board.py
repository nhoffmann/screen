import socket
import json

def send_to_board(board_address, arr):
    data_string = json.dumps(arr)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(board_address)
        s.sendall(data_string.encode())

    
