#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run an OSC server with asynchroneous I/O handling via the uasync framwork.
"""

import sys
import logging
import socket

from uasyncio.core import IORead, coroutine, get_event_loop, sleep

from uosc.socketutil import get_hostport
from uosc.server import handle_osc

MAX_DGRAM_SIZE = 1472
log = logging.getLogger("uosc.async_server")


def run_server(host, port, client_coro, **params):
    if __debug__: log.debug("run_server(%s, %s)", host, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))

    try:
        while True:
            if __debug__: log.debug("run_server: Before IORead")
            yield IORead(sock)
            if __debug__: log.debug("run_server: Before recvfrom")
            data, caddr = sock.recvfrom(MAX_DGRAM_SIZE)
            if __debug__: log.debug("RECV %i bytes from %s:%s",
                                    len(data), *get_hostport(caddr))
            yield client_coro(data, caddr, **params)
    finally:
        sock.close()
        log.info("Bye!")


@coroutine
def serve(data, caddr, **params):
    if __debug__: log.debug("Client request handler coroutine called.")
    handle_osc(data, caddr, **params)
    # simulate long running request handler
    yield from sleep(1)
    if __debug__: log.debug("Finished processing request,")


class Counter:
    def __init__(self):
        self.count = 0

    def __call__(self, t, msg):
        self.count += 1
        print("OSC message from: udp://%s:%s" % get_hostport(msg[3]))
        print("OSC address:", msg[0])
        print("Type tags:", msg[1])
        print("Arguments:", msg[2])
        print()


if __name__ == '__main__':
    import time
    logging.basicConfig(
        level=logging.DEBUG if '-v' in sys.argv[1:] else logging.INFO)
    loop = get_event_loop()
    counter = Counter()
    loop.call_soon(run_server("0.0.0.0", 9001, serve, dispatch=counter))
    if __debug__: log.debug("Starting asyncio event loop")
    start = time.time()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
        reqs = counter.count / (time.time() - start)
        print("Requests/second: %.2f" % reqs)
