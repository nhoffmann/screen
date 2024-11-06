import cv2
import threading
from time import sleep
import board

IP_1 = '192.168.1.224'
IP_2 = '192.168.1.93'
PORT = 50_000

board_1 = board.Board(board.BOARD_8_32, IP_1)
board_2 = board.Board(board.BOARD_8_32, IP_2)

VIDEO_FILE = "../../assets/colors_rotated_smaller_contrast.mp4"

WIDTH = 8
HEIGHT = 32

while True:
    cap = cv2.VideoCapture(VIDEO_FILE)

    okay, frame = cap.read()
    frame_number = 0
    print(f'# Video appears to be {len(frame[0])} x {len(frame)}')


    arr1 = [(0, 0, 0)] * 256
    arr2 = [(0, 0, 0)] * 256
    # Process each frame.
    while okay:
        limit = 256
        index_1 = 0
        index_2 = 0
        for row in frame:
            pixel_index = 0
            for pixel in row:
                if pixel_index < WIDTH:
                    arr1[index_1] = (int(pixel[0]), int(pixel[1]), int(pixel[2]))
                    index_1 += 1
                else:
                    arr2[index_2] = (int(pixel[0]), int(pixel[1]), int(pixel[2]))
                    index_2 += 1
                
                pixel_index += 1
                
                if pixel_index == WIDTH * 2: break
                if index_1 == limit or index_2 == limit: break
            if index_1 == limit or index_2 == limit: break
            index_1 += 1
            index_2 += 1
        
        board_1.pixel_array = arr1
        board_2.pixel_array = arr2

        thread_1 = threading.Thread(target=board_1.send)
        thread_1.start()
        thread_2 = threading.Thread(target=board_2.send)
        thread_2.start()

        print("Processed frame: ", frame_number)
        frame_number += 1

        sleep(0.04)
        okay, frame = cap.read()
