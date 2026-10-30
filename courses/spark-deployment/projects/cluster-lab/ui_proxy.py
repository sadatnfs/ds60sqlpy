"""Bounded byte relay for fixed Spark/Jupyter UI destinations only."""

import selectors
import signal
import socket
import socketserver
import sys
import threading
import time

DESTINATIONS = {
    8080: ("master", 8080),
    4040: ("driver", 4040),
    18080: ("history", 18080),
    8888: ("notebook", 8888),
    14040: ("notebook", 4040),
}
CAPACITY = threading.BoundedSemaphore(16)


class Relay(socketserver.BaseRequestHandler):
    def handle(self):
        if not CAPACITY.acquire(blocking=False):
            return
        try:
            destination = DESTINATIONS[self.server.server_address[1]]
            with socket.create_connection(destination, timeout=5) as upstream:
                sockets = (self.request, upstream)
                for stream in sockets:
                    stream.settimeout(15)
                with selectors.DefaultSelector() as selector:
                    selector.register(self.request, selectors.EVENT_READ, upstream)
                    selector.register(upstream, selectors.EVENT_READ, self.request)
                    deadline = time.monotonic() + 600
                    while time.monotonic() < deadline:
                        events = selector.select(timeout=5)
                        for key, _ in events:
                            payload = key.fileobj.recv(16_384)
                            if not payload:
                                return
                            key.data.sendall(payload)
        except (OSError, TimeoutError):
            # Do not log request bytes, headers, notebook tokens or URLs.
            return
        finally:
            CAPACITY.release()


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def process_request(self, request, client_address):
        if threading.active_count() >= 40:
            self.shutdown_request(request)
            return
        super().process_request(request, client_address)


def main():
    servers = [Server(("0.0.0.0", port), Relay) for port in DESTINATIONS]
    for server in servers:
        threading.Thread(target=server.serve_forever, daemon=True).start()
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    try:
        while True:
            signal.pause()
    finally:
        for server in servers:
            server.server_close()


if __name__ == "__main__":
    main()
