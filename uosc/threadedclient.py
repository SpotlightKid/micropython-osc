# -*- coding: utf-8 -*-
"""OSC client running in a separate thread.

Communicates with the main thread via a queue. Provides the same API as the
non-threaded client, with a few threading-related extensions:

    from uosc.threadedclient import ThreadedClient

    # start=True starts the thread immediately
    osc = ThreadedClient('192.168.0.42', 9001, start=True)

    # if the OSC message can not placed in the queue within timeout
    # raises a queue.Full error
    osc.send('/pi', 3.14159, timeout=1.0)
    # Stops and joins the thread and closes the client socket
    osc.close()

"""

import logging
import threading

try:
    import queue
except ImportError:
    import Queue as queue

from uosc.client import Client


log = logging.getLogger(__name__)


class ThreadedClient(threading.Thread):
    def __init__(self, host, port=None, start=False, timeout=3.0):
        super(ThreadedClient, self).__init__()
        self.host = host
        self.port = port
        self.timeout = timeout
        self._q = queue.Queue()

        if start:
            self.start()

    def run(self, *args, **kw):
        self.client = Client((self.host, self.port))

        while True:
            msg = self._q.get()
            if msg is None:
                break

            addr, msg = msg
            log.debug("Sending OSC msg %s, %r", addr, msg)
            self.client.send(addr, *msg)

        self.client.close()

    def send(self, addr, *args, **kw):
        self._q.put((addr, args), timeout=kw.get('timeout', self.timeout))

    def close(self, **kw):
        timeout = kw.get('timeout', self.timeout)
        log.debug("Emptying send queue...")

        while True:
            try:
                self._q.get_nowait()
            except queue.Empty:
                break

        if self.is_alive():
            log.debug("Signalling OSC client thread to exit...")
            self._q.put(None, timeout=timeout)

            log.debug("Joining OSC client thread...")
            self.join(timeout)

            if self.is_alive():
                log.warning("OSC client thread still alive after join().")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
