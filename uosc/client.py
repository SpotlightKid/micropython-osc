import usocket as socket

from .common import create_message


def send(dest, address, *args):
    Client(dest).send(address, *args)


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

    def __del__(self):
        if self.sock:
            self.sock.close()
