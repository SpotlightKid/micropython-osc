# -*- coding: utf-8 -*-
"""Simple OSC client."""

import socket

from uosc.common import create_message


def send(dest, address, *args):
    with Client(dest) as client:
        client.send(address, *args)


class Client:
    def __init__(self, dest):
        self.dest = socket.getaddrinfo(*dest)[0][4]
        self.sock = None

    def send(self, address, *args, **kw):
        dest = kw.get('dest', self.dest)

        if isinstance(dest, tuple):
            dest = socket.getaddrinfo(*dest)[0][4]

        if not self.sock:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.sock.sendto(create_message(address, *args), dest)

    def close(self):
        if self.sock:
            self.sock.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

