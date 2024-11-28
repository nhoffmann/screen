import network
import socket
import select
import json
import struct
import time

_DEFAULT_PORT = const(50_000)
_DEFAULT_NUM_CONNECTIONS = const(50)
_DEFAULT_BUFFER_SIZE = const(
    8192
)  # arbitrary multiple of 2, should probably be around the max size of all the boards

_MESSAGE_HEADER_LEN = const(2)
_HEADER_MARKER = const(">H")

_READ_ONLY = select.POLLIN | select.POLLHUP | select.POLLERR


def device_ip():
    sta_if = network.WLAN(network.STA_IF)
    return sta_if.ipconfig("addr4")[0]


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

    def read(self):
        self._read_data_from_socket()

        if not self._content_length:
            self._process_protoheader()

        if self._content_length and len(self._receive_buffer) >= self._content_length:
            self._process_request()

    def _read_data_from_socket(self):
        try:
            data = self.socket.recv(self._buffer_size)
        except:
            pass
        else:
            if data:
                self._receive_buffer += data
                # print("Received data: ", len(self._receive_buffer))
                # print("Free memory: ", gc.mem_free())
                # print("Allocated memory: ", gc.mem_alloc())
            else:
                raise RuntimeError("Peer closed")

    def _process_protoheader(self):
        if len(self._receive_buffer) >= _MESSAGE_HEADER_LEN:
            self._content_length = struct.unpack(
                _HEADER_MARKER, self._receive_buffer[:_MESSAGE_HEADER_LEN]
            )[0]
            self._receive_buffer = self._receive_buffer[_MESSAGE_HEADER_LEN:]

    def _process_request(self):
        # start = time.ticks_us()
        num_pixels = self._content_length // 3
        pixel_format = "BBB" * num_pixels
        flat_pixels = struct.unpack(
            pixel_format, self._receive_buffer[: self._content_length]
        )
        self.request = [
            tuple(flat_pixels[i : i + 3]) for i in range(0, len(flat_pixels), 3)
        ]
        # print(f"Processing request takes: {time.ticks_us() - start} us")
        self.close()

    def write(self):
        print("Socket wants to send data")

    def close(self):
        try:
            self.poller.unregister(self.socket)
        except Exception as e:
            print(f"Error: poll.unregister() exception for " f"{self.address}: {e!r}")

        try:
            self.socket.close()
        except OSError as e:
            print(f"Error: socket.close() exception for {self.address}: {e!r}")
        finally:
            # Delete reference to socket object for garbage collection
            self.socket = None
            # Delete receive buffer for garbage collection
            self._receive_buffer = None


class TcpServer:
    def __init__(
        self,
        ip_address=None,
        port=_DEFAULT_PORT,
        num_connections=_DEFAULT_NUM_CONNECTIONS,
        buffer_size=_DEFAULT_BUFFER_SIZE,
    ):
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

        self._poller.register(self._socket, _READ_ONLY)
        self._message_map = {}

        print(f"TCP server listening on: {(self._ip_address, self._port)}")

    def handle_requests(self, callback):
        while True:
            events = self._poller.poll()

            for event_socket, event_mask in events:
                event_socket_fileno = event_socket.fileno()
                if event_socket is self._socket:
                    self._accept_connection()
                else:
                    message = self._message_map[event_socket_fileno]
                    try:
                        message.process_events(event_mask)
                        if message.request:
                            # We have a complete message to process. Send it to the callback
                            callback(message.request)
                            del self._message_map[event_socket_fileno]
                            # gc.collect()
                            # pass
                    except Exception as e:
                        print(f"Error: Exception for {message.address}: {e}")
                        try:
                            message.close()
                        except:
                            pass
                        del self._message_map[event_socket_fileno]

    def _accept_connection(self):
        try:
            connection, address = self._socket.accept()
            connection.setblocking(False)
            message = Message(self._poller, connection, address, self._buffer_size)
            self._poller.register(connection, _READ_ONLY)
            self._message_map[connection.fileno()] = message
            # print("Message map length: ", len(self._message_map))
        except Exception as e:
            print(f"Error during accepting the connection: {e}")
