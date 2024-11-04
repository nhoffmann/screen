import cv2
from time import sleep
from send_to_board import send_to_board

IP_1 = '192.168.1.224'
IP_2 = '192.168.1.93'
PORT = 50_000

BOARD_1 = (IP_1, PORT)
BOARD_2 = (IP_2, PORT)

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
        
        # print(arr)
        send_to_board(BOARD_1, arr1)
        send_to_board(BOARD_2, arr2)

        print("Processed frame: ", frame_number)
        frame_number += 1

        sleep(0.01)
        okay, frame = cap.read()
