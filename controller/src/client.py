import selectors
import json
import struct
import logging
import socket
import threading

log = logging.getLogger(__name__)

DEFAULT_BUFFER_SIZE = 8192


class Message:
    def __init__(self, selector, sock, address, request, buffer_size):
        self.selector = selector
        self.socket = sock
        self.address = address
        self.request = request
        self._buffer_size = buffer_size
        self._send_buffer = b""
        self._request_queued = False

    def process_events(self, event_mask):
        if event_mask & selectors.EVENT_WRITE:
            self.write()

    def write(self):
        if not self._request_queued:
            self.queue_request()

        self._write_to_socket()

        if self._request_queued and not self._send_buffer:
            # we have a request queued and the send buffer is empty, so
            # we're done writing
            self.close()
            # self.selector.modify(self.socket, selectors.EVENT_READ, self)

    def queue_request(self):
        # encoded_payload = self._json_encode(self.request)
        self._send_buffer = self._create_message(self.request)
        self._request_queued = True

    def close(self):
        try:
            self.selector.unregister(self.socket)
        except Exception as e:
            log.error(
                f"Error: selector.unregister() exception for {self.address}: {repr(e)}"
            )

        try:
            self.socket.close()
        except OSError as e:
            log.error(f"Error: socket.close() exception for {self.address}: {repr(e)}")
        finally:
            pass
            # self.socket = None

    def _write_to_socket(self):
        # write data to the socket as long as we have data in the send buffer
        if self._send_buffer:
            try:
                sent = self.socket.send(self._send_buffer)
                log.debug(f"Sent {sent} bytes")
            except Exception as e:
                # log.error(f"BlockingIOError: {e}")
                log.error(f"Error writing to socket: {e}")
                pass
            else:
                # this should empty the send buffer when all data has been sent
                self._send_buffer = self._send_buffer[sent:]

    def _json_encode(self, obj):
        return json.dumps(obj).encode()

    def _create_message(self, payload):
        flat_payload = [val for pixel in payload for val in pixel]

        message_header = struct.pack(">H", len(flat_payload))

        pixel_format = "B" * len(flat_payload)
        message_content = struct.pack(pixel_format, *flat_payload)

        return message_header + message_content


class TcpClient:
    def __init__(self, address, port, buffer_size=DEFAULT_BUFFER_SIZE):
        self.address = address
        self.port = port
        self._buffer_size = buffer_size

        self._selector = selectors.DefaultSelector()

        threading.Thread(target=self.handle_events, daemon=True).start()

        log.info(f"Initialized TCP Client: {self.address}:{self.port}")

    def handle_events(self):
        while True:
            events = self._selector.select()
            for key, mask in events:
                message = key.data
                try:
                    message.process_events(mask)
                except Exception as e:
                    log.error(f"Error sending payload: {e}")
                    # message.close()
            # if not self._selector.get_map():
            #     break

    def send(self, payload):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self._buffer_size)
        sock.setblocking(False)
        sock.connect_ex((self.address, self.port))

        message = Message(
            self._selector,
            sock,
            (self.address, self.port),
            payload,
            self._buffer_size,
        )

        self._selector.register(sock, selectors.EVENT_WRITE, data=message)
