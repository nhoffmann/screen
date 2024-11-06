import network
import socket
import select
import json
import struct
import utime as time

DEFAULT_PORT = 50_000
DEFAULT_NUM_CONNECTIONS = 10
DEFAULT_BUFFER_SIZE = 4096 #8192 # arbitrary multiple of 2, should probably be around the max size of all the boards

POLL_TIMEOUT = 1000
MESSAGE_HEADER_LEN = 2

READ_ONLY = ( select.POLLIN |
            select.POLLHUP |
            select.POLLERR )
READ_WRITE = READ_ONLY | select.POLLOUT

def device_ip():
    sta_if = network.WLAN(network.STA_IF)
    return sta_if.ipconfig('addr4')[0]

class Message:
    def __init__(self, poller, sock, address, buffer_size):
        self.poller = poller
        self.socket = sock
        self.address = address 
        self._buffer_size = buffer_size

        self._receive_buffer = b""
        self._content_length = None
        self.request = None

    def process_events(self, event_mask):
        if event_mask & select.POLLIN:
            self.read()
        if event_mask & select.POLLOUT:
            self.write()
        if event_mask & select.POLLHUP:
            print("Client hung up")
        if event_mask & select.POLLERR:
            print("An error occured")

    def _read(self):
        try:
            data = self.socket.recv(self._buffer_size)
        except:
            pass 
        else:
            if data:
                self._receive_buffer += data
            else: 
                raise RuntimeError("Peer closed")

    def read(self):
        self._read()

        if self._content_length is None:
            self._process_protoheader()

        if self._content_length is not None:
            self.process_request()

    def _process_protoheader(self):
        if len(self._receive_buffer) >= MESSAGE_HEADER_LEN:
            self._content_length = struct.unpack(">H", self._receive_buffer[:MESSAGE_HEADER_LEN])[0]
            self._receive_buffer = self._receive_buffer[MESSAGE_HEADER_LEN:]

    def process_request(self):
        if not len(self._receive_buffer) >= self._content_length:
            # print(f"Weird state {len(self._receive_buffer)} >= {self._content_length}")
            ## TODO I don't understand this yet
            # something like we have not read all the data so return early
            return
        # print(f"{len(self._receive_buffer)} >= {self._content_length}") 
        data = self._receive_buffer[:self._content_length]
        # print(f"data = {data}")
        self._receive_buffer = self._receive_buffer[self._content_length:]
        # print(f"self._receive_buffer = {self._receive_buffer}")
        # self.request = self._hexarray_decode(data)
        # print(f"self.request = {self.request}")
        self.request = self._json_decode(data)

    def write(self):
        print("Socket wants to send data")

    def _json_decode(self, json_bytes):
        obj = json.loads(json_bytes)
        return obj
    
    def _hexarray_decode(self, hexarray_bytes):
        hex_string = hexarray_bytes.decode("utf-8")
        step = 6
        # return [self._hex2rgb(hex_string[i:i+step]) for i in range(0, len(hex_string), step)] 
        t = time.ticks_us()
        hex_arr = [hex_string[i:i+step] for i in range(0, len(hex_string), step)] 
        color_array = []
        for hexcode in hex_arr:
            color_array.append(self._hex2rgb(hexcode))
        delta = time.ticks_diff(time.ticks_us(), t)
        print(f"Time to decode the hexarray: {delta/1000}ms")
        return color_array

    def _hex2rgb(self, hexcode):
        t = time.ticks_us()

        # result = tuple(int(hexcode[i:i+2], 16) for i in (0, 2, 4))
        
        result = ( int(hexcode[0:2], 16), int(hexcode[2:4], 16), int(hexcode[4:6], 16) )

        delta = time.ticks_diff(time.ticks_us(), t)
        print(f"Time to decode the hexstring: {delta/1000}ms")
        return result
        
    def close(self):
        try:
            self.poller.unregister(self.socket)
        except Exception as e:
            print(
                f"Error: poll.unregister() exception for "
                f"{self.address}: {e!r}"
            )

        try:
            self.socket.close()
        except OSError as e:
            print(f"Error: socket.close() exception for {self.address}: {e!r}")
        finally:
            # Delete reference to socket object for garbage collection
            self.socket = None


class TcpServer:
    def __init__(self, ip_address = None, port = DEFAULT_PORT, num_connections = DEFAULT_NUM_CONNECTIONS, buffer_size = DEFAULT_BUFFER_SIZE):
        if ip_address:
            self._ip_address = ip_address
        else:
            self._ip_address = device_ip()

        self._port = port 
        self._num_connections = num_connections
        self._buffer_size = buffer_size
        self._poller = select.poll()

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((self._ip_address, self._port))
        self._socket.listen(self._num_connections)
        self._socket.setblocking(False)

        self._poller.register(self._socket, READ_ONLY)
        self._message_map = {}

        print(f"TCP server listening on: {(self._ip_address, self._port)}")

    def handle_requests(self, callback):
        while True:
            events = self._poller.poll()

            for event_socket, event_mask in events:
                if event_socket is self._socket:
                    self._accept_connection()
                else:
                    message = self._message_map[event_socket.fileno()]
                    try:
                        message.process_events(event_mask)
                        if message.request is not None:
                            callback(message.request)
                    except Exception as e:
                        print(f"Error: Exception for {message.address}: {e}")
                    finally:
                        message.close()

    def _accept_connection(self):
        try:
            connection, address = self._socket.accept()
            connection.setblocking(False)
            message = Message(self._poller, connection, address, self._buffer_size)
            self._poller.register(connection, READ_ONLY)
            self._message_map[connection.fileno()] = message
        except Exception as e:
            print(f"Error during accepting the connection: {e}")
