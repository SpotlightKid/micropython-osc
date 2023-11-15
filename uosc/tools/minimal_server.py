#!/usr/bin/env python
"""A minimal, blocking OSC UDP server."""

try:
    import socket
except ImportError:
    import usocket as socket

try:
    import logging
except ImportError:
    import uosc.compat.fakelogging as logging

if __debug__:
    from uosc.compat.socketutil import get_hostport

from uosc.server import handle_osc


log = logging.getLogger("uosc.minimal_server")
DEFAULT_ADDRESS = '0.0.0.0'
DEFAULT_PORT = 9001
MAX_DGRAM_SIZE = 1472


def run_server(saddr, port, handler=handle_osc):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ai = socket.getaddrinfo(saddr, port)[0]
    sock.bind(ai[-1])
    log.info("Listening for OSC messages on %s:%i.", saddr, port)

    try:
        while True:
            data, caddr = sock.recvfrom(MAX_DGRAM_SIZE)
            if __debug__: log.debug("RECV %i bytes from %s:%s",
                                    len(data), *get_hostport(caddr))
            handler(data, caddr)
    finally:
        sock.close()
        log.info("Bye!")


def main(args=None):
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument('-v', '--verbose', action="store_true",
                    help="Enable debug logging")
    ap.add_argument('-a', '--address', default=DEFAULT_ADDRESS,
                    help="OSC server address (default: %s)" % DEFAULT_ADDRESS)
    ap.add_argument('-p', '--port', type=int, default=DEFAULT_PORT,
                    help="OSC server port (default: %s)" % DEFAULT_PORT)

    args = ap.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    try:
        run_server(args.address, int(args.port))
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    import sys
    sys.exit(main() or 0)
