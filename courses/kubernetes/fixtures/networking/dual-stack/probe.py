"""Require a real version response over each explicitly selected address family."""
from __future__ import annotations

import argparse
import http.client
from ipaddress import IPv6Address, ip_address
import json
import socket

EXPECTED = b'ds60-dualstack-v1\n'


def probe(address: str, port: int, family: int) -> dict[str, str]:
    parsed = ip_address(address)
    expected_version = 4 if family == socket.AF_INET else 6 if family == socket.AF_INET6 else 0
    if (parsed.version != expected_version or not parsed.is_private
            or parsed.is_multicast or parsed.is_unspecified
            or isinstance(parsed, IPv6Address) and parsed.ipv4_mapped is not None):
        raise ValueError('Use the matching private/loopback literal from the owned lab receipt.')
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError('Use a valid owned listener port.')
    connection = http.client.HTTPConnection(address, port, timeout=3)
    stream = socket.socket(family, socket.SOCK_STREAM)
    stream.settimeout(3)
    try:
        stream.connect((address, port))
        connection.sock = stream
        connection.request('GET', '/version', headers={'Connection': 'close'})
        response = connection.getresponse()
        body = response.read(128)
        if response.status != 200 or body != EXPECTED:
            raise ValueError('The selected family did not return the expected version response.')
        return {'family': 'IPv4' if family == socket.AF_INET else 'IPv6', 'status': 'passed', 'version': EXPECTED.decode().strip()}
    finally:
        connection.close()
        stream.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ipv4', required=True)
    parser.add_argument('--ipv6', required=True)
    parser.add_argument('--port', type=int, default=80)
    args = parser.parse_args()
    results = [probe(args.ipv4, args.port, socket.AF_INET), probe(args.ipv6, args.port, socket.AF_INET6)]
    print(json.dumps({'status': 'passed', 'results': results}, sort_keys=True))


if __name__ == '__main__':
    main()
