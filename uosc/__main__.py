#!/usr/bin/env micropython
# -*- coding: utf-8 -*-

import argparse
import logging
import sys

from uosc.server import run_server


DEFAULT_ADDRESS = '0.0.0.0'
DEFAULT_PORT = 9001


def main(args=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('-v', '--verbose', action="store_true",
                    help="Enable debug logging")
    ap.add_argument('-a', '--address', default=DEFAULT_ADDRESS,
                    help="OSC server address (default: %s)" % DEFAULT_ADDRESS)
    ap.add_argument('-p', '--port', type=int, default=DEFAULT_PORT,
                    help="OSC server port (default: %s)" % DEFAULT_PORT)

    args = ap.parse_args(args if args is not None else sys.argv[1:])
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    try:
        run_server(args.address, int(args.port))
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
