"""Optional manual dual-stack teaching app; ordinary course fixture is unchanged."""
from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import signal
import socket
import socketserver
import threading

VERSION = b"ds60-dualstack-v1\n"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        status, body = (200, VERSION) if self.path == '/version' else (200, b'ready\n') if self.path == '/ready' else (404, b'not found\n')
        self.send_response(status)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)


class DualStackServer(ThreadingHTTPServer):
    address_family = socket.AF_INET6

    def server_bind(self) -> None:
        # IPv4-mapped connections are accepted by this IPv6 socket on a capable
        # Linux kernel. A missing capability raises rather than falling back.
        self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        socketserver.TCPServer.server_bind(self)
        self.server_name = 'dual-stack-study'
        self.server_port = self.server_address[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bind', choices=['::1', '::'], default='::1')
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('Choose a port from 1 through 65535.')
    if not socket.has_dualstack_ipv6():
        raise SystemExit('This prepared kernel does not support dual-stack IPv6 sockets.')
    server = DualStackServer((args.bind, args.port), Handler)
    def stop(signum: int, frame: object) -> None:
        threading.Thread(target=server.shutdown, daemon=True).start()
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        server.serve_forever(poll_interval=0.2)
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
