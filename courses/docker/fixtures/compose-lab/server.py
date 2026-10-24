"""Small single-process local Docker study fixture; no external dependencies."""
from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import socketserver
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DATA = Path('/data')
LOCK = threading.Lock()


def read_counter() -> int:
    path = DATA / 'counter.json'
    if not path.exists():
        return 0
    value = json.loads(path.read_text(encoding='utf-8'))
    if (not isinstance(value, dict) or type(value.get('schema_version')) is not int
            or value['schema_version'] != 1 or type(value.get('counter')) is not int
            or value['counter'] < 0):
        raise ValueError('invalid counter state; preserve it for recovery')
    return value['counter']


def increment() -> int:
    with LOCK:
        value = read_counter() + 1
        temporary = DATA / 'counter.next'
        temporary.write_text(json.dumps({'schema_version': 1, 'counter': value}) + '\n', encoding='utf-8')
        temporary.replace(DATA / 'counter.json')
        return value


class Handler(BaseHTTPRequestHandler):
    def respond(self, status: int, value: dict[str, object]) -> None:
        body = (json.dumps(value, sort_keys=True) + '\n').encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == '/healthz':
            self.respond(200, {'status': 'ready'})
        elif self.path == '/':
            self.respond(200, {'message': os.environ.get('APP_MESSAGE', 'hello from Docker study')})
        elif self.path == '/counter':
            with LOCK:
                value = read_counter()
            self.respond(200, {'counter': value, 'schema_version': 1})
        else:
            self.respond(404, {'error': 'unknown route'})

    def do_POST(self) -> None:
        if self.path != '/increment':
            self.respond(404, {'error': 'unknown route'})
            return
        if self.headers.get('Content-Length', '0') != '0':
            self.respond(400, {'error': 'this fixture accepts an empty body only'})
            return
        self.respond(200, {'counter': increment(), 'schema_version': 1})


class LocalServer(ThreadingHTTPServer):
    def server_bind(self) -> None:
        socketserver.TCPServer.server_bind(self)
        self.server_name = 'docker-study'
        self.server_port = self.server_address[1]


def main() -> None:
    DATA.mkdir(exist_ok=True)
    read_counter()
    server = LocalServer(('0.0.0.0', 8080), Handler)
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
