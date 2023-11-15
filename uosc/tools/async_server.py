#!/usr/bin/env python
"""Run an OSC server with asynchroneous I/O handling via the uasync framwork.

Note: you can run this with the unix port from the root directory of the
repo like this:

With micropython (unix port)

    MICROPYPATH=".frozen:$(pwd).$(pwd)/examples" micropython uosc/tools/async_server.py -v

With CPython (or PyPy etc.)

    PYTHONPATH="$(pwd)" python -m uosc.tools.async_server.py -v

Then send OSC messages to localhost port 9001, for example with oscsend::

    oscsend localhost 9001 /foo ifs $i 3.141 "hello world!"

"""

try:
    import socket
except ImportError:
    import usocket as socket

try:
    import select
except ImportError:
    import uselect as select

try:
    import asyncio
except ImportError:
    import uasyncio as asyncio

from uosc.server import handle_osc

if __debug__:
    from uosc.compat.socketutil import get_hostport

try:
    import logging
except ImportError:
    import uosc.compat.fakelogging as logging


log = logging.getLogger("uosc.async_server")
DEFAULT_ADDRESS = '0.0.0.0'
DEFAULT_PORT = 9001
MAX_DGRAM_SIZE = 1472


class UDPServer:
    def __init__(self, poll_timeout=1, max_packet_size=MAX_DGRAM_SIZE, poll_interval=0.0):
        self.poll_timeout = poll_timeout
        self.max_packet_size = max_packet_size
        self.poll_interval = poll_interval

    def close(self):
        self.sock.close()

    async def serve(self, host, port, cb, **params):
        # bind instance attributes to local vars
        interval = self.poll_interval
        maxsize = self.max_packet_size
        timeout = self.poll_timeout

        if __debug__: log.debug("Starting UDP server @ (%s, %s)", host, port)
        ai = socket.getaddrinfo(host, port)[0]  # blocking!
        self.sock = s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setblocking(False)
        s.bind(ai[-1])

        p = select.poll()
        p.register(s, select.POLLIN)
        poll = getattr(p, "ipoll", p.poll)

        if __debug__: log.debug("Entering polling loop...")
        while True:
            try:
                for res in poll(timeout):
                    if res[1] & (select.POLLERR | select.POLLHUP):
                        if __debug__: log.debug("UDPServer.serve: unexpected socket error.")
                        break
                    elif res[1] & select.POLLIN:
                        if __debug__: log.debug("UDPServer.serve: Before recvfrom")
                        buf, addr = s.recvfrom(maxsize)
                        if __debug__: log.debug("RECV %i bytes from %s:%s", len(buf),
                                                *get_hostport(addr))
                        asyncio.create_task(cb(res[0], buf, addr, **params))

                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                if __debug__: log.debug("UDPServer.serve task cancelled.")
                break

        # Shutdown server
        s.close()
        log.info("Bye!")


async def serve_request(sock, data, caddr, **params):
    if __debug__: log.debug("Client request handler coroutine called.")
    handle_osc(data, caddr, **params)
    # simulate long running request handler
    await asyncio.sleep(1)
    if __debug__: log.debug("Finished processing request.")


class Counter:
    def __init__(self, debug=False):
        self.count = 0
        self.debug = debug

    def __call__(self, t, msg):
        self.count += 1
        if self.debug:
            print("OSC message from: udp://%s:%s" % get_hostport(msg[3]))
            print("OSC address:", msg[0])
            print("Type tags:", msg[1])
            print("Arguments:", msg[2])
            print()


def main():
    import sys
    import time

    debug = '-v' in sys.argv[1:]

    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO)

    server = UDPServer(poll_timeout=50)
    counter = Counter(debug=debug)

    if __debug__: log.debug("Starting asyncio event loop")
    start = time.time()

    try:
        asyncio.run(server.serve(DEFAULT_ADDRESS, DEFAULT_PORT, serve_request, dispatch=counter))
    except KeyboardInterrupt:
        pass
    finally:
        reqs = counter.count / (time.time() - start)
        print("Requests/second: %.2f" % reqs)
        print("Requests total: %i" % counter.count)


if __name__ == '__main__':
    import sys
    sys.exit(main() or 0)
