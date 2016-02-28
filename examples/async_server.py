import logging
import socket
from uasyncio.core import *

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
    handle_osc(data, caddr, **params)
    if __debug__: log.debug("Finished processing request")

def printer(t, msg):
    print(t, msg)


logging.basicConfig(level=logging.INFO)
loop = get_event_loop()
loop.call_soon(run_server("0.0.0.0", 9001, serve, dispatch=printer))
loop.run_forever()
loop.close()
