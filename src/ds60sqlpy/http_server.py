"""HTTP server binding that stays independent of DNS availability.

The standard HTTPServer performs a reverse lookup only to populate its display
name. Local classrooms and private workers already validate their bound origin;
using the actual bound address avoids an unnecessary network-dependent startup.
"""

from __future__ import annotations

from http.server import HTTPServer
from socketserver import TCPServer, ThreadingMixIn


class LocalHTTPServer(HTTPServer):
    def server_bind(self) -> None:
        TCPServer.server_bind(self)
        host, port = self.server_address[:2]
        self.server_name = str(host)
        self.server_port = int(port)


class LocalThreadingHTTPServer(ThreadingMixIn, LocalHTTPServer):
    daemon_threads = True
