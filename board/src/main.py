from machine import Pin
from neopixel import NeoPixel
import socket, json
import network
import select

WIDTH = 8
HEIGHT = 32
NUM_PIXELS = WIDTH * HEIGHT
OFF = (0, 0, 0)
SERVER_PORT = 50000
NUM_CONNECTIONS = 10

POLL_TIMEOUT = 1000
RECV_SIZE = 8192 # arbitrary multiple of 2, should probably be the max size of a 256 item json array
READ_ONLY = ( select.POLLIN |
            select.POLLHUP |
            select.POLLERR )
READ_WRITE = READ_ONLY | select.POLLOUT

def create_led_matrix():
    pin = Pin(2, Pin.OUT) 
    np = NeoPixel(pin, NUM_PIXELS, bpp=3)

    return np
    
def blackout(np):
    for i in range(HEIGHT * WIDTH):		
        np[i] = OFF
    np.write()

def server_ip():
    sta_if = network.WLAN(network.STA_IF)
    return sta_if.ipconfig('addr4')[0]

def create_and_start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(False)
    server_addresss = (server_ip(), SERVER_PORT)
    try:
        server.bind(server_addresss)
        server.listen(NUM_CONNECTIONS)
    except OSError as e:
        print("Cannot start server: ", e)

    return server

def create_poller(server):
    poller = select.poll()
    poller.register(server, READ_ONLY)

    return poller

def close_connection(poller, socket):
    poller.unregister(socket)
    socket.close() 

def start_event_loop(server, poller, np):
    try:
        while True:
            events = poller.poll(POLL_TIMEOUT)

            for sock, flag in events:
                if flag & select.POLLIN:
                    if sock is server:
                        connection, client_address = sock.accept()
                        connection.setblocking(False)
                        poller.register(connection, READ_ONLY)
                    else:
                        data = sock.recv(RECV_SIZE)
                        if data:
                            try:
                                arr = json.loads(data)
                                for i in range(len(arr)):
                                    np[i] = arr[i]
                                np.write()
                            except Exception as e:
                                print(f"{e}")

                        else:
                            close_connection(poller, sock)
                elif flag & select.POLLHUP:
                    # Client hung up
                    close_connection(poller, sock)
                elif flag & select.POLLOUT:
                    # Socket is ready to send data
                    print("Socket is ready to send data")
                elif flag & select.POLLERR:
                    # an error occured
                    close_connection(poller, sock)
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting...")
        blackout(np)
        print("Server stopped.")


print("Initializing LED matrix")
led_matrix = create_led_matrix()
print("Turn all LEDs off")
blackout(led_matrix)

print("Starting the server")
server = create_and_start_server()
print("Server started.")
print("Creating the poller")
poller = create_poller(server)
print("Start server event loop")
start_event_loop(server, poller, led_matrix)
