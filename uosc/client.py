# -*- coding: utf-8 -*-
"""Simple OSC client."""

import socket

from struct import pack

from uosc.common import to_frac


TYPE_MAP = {
    int: 'i',
    float: 'f',
    str: 's',
    bytes: 'b',
    bytearray: 'b',
    True: 'T',
    False: 'F',
    None: 'N',
}


def pack_timetag(t):
    """Pack an OSC timetag into 64-bit binary blob."""
    return pack('>II', *to_frac(t))


def pack_string(s):
    """Pack a string into a binary OSC string."""
    s = s.encode('ascii', 'strict') + b'\0'

    assert all(i < 128 for i in s), "OSC strings may only contain ASCII chars."

    if len(s) % 4:
        s += b'\0' * (4 - len(s) % 4)

    return s


def pack_blob(b, encoding='utf-8'):
    """Pack a bytes, bytearray or tuple/list of ints into a binary OSC blob."""
    if isinstance(b, (tuple, list)):
        b = bytearray(b)
    elif isinstance(b, str):
        b = bytes(b, encoding)

    b = pack('>I', len(b)) + b

    if len(b) % 4:
        b += b'\0' * (4 - len(b) % 4)

    return b


def create_message(address, *args):
    """Create an OSC message with given address pattern and arguments.

    The OSC types are either inferred from the Python types of the arguments,
    or you can pass arguments as 2-item tuples with the OSC typetag as the
    first item and the argument value as the second. Python objects are mapped
    to OSC typetags as follows:

    * ``int``: i
    * ``float``: f
    * ``str``: s
    * ``bytes`` / ``bytearray``: b
    * ``None``: N
    * ``True``: T
    * ``False``: F

    If you want to encode a Python object to another OSC type, you have to pass
    a ``(typetag, data)`` tuple, where ``data`` must be of the appropriate type
    according to the following table:

    * c: ``str`` of length 1
    * h: ``int``
    * d: ``float``
    * I: ``None`` (unused)
    * m: ``tuple / list`` of 4 ``int``s or ``bytes / bytearray`` of length 4
    * r: same as 'm'
    * t: OSC timetag as as ``int / float`` seconds since the NTP epoch
    * S: ``str``

    """
    assert address.startswith('/'), "Address pattern must start with a slash."

    data = []
    types = [',']

    for arg in args:
        type_ = type(arg)

        if isinstance(arg, tuple):
            typetag, arg = arg
        else:
            typetag = TYPE_MAP.get(type_) or TYPE_MAP.get(arg)

        if typetag in 'ifd':
            data.append(pack('>' + typetag, arg))
        elif typetag in 'sS':
            data.append(pack_string(arg))
        elif typetag == 'b':
            data.append(pack_blob(arg))
        elif typetag in 'rm':
            data.append(pack('BBBB', *tuple(arg)))
        elif typetag == 'c':
            data.append(pack('>I', ord(arg)))
        elif typetag == 'h':
            data.append(pack('>q', arg))
        elif typetag == 't':
            data.append(pack_timetag(arg))
        elif typetag not in 'IFNT':
            raise TypeError("Argument of type '%s' not supported." % type_)

        types.append(typetag)

    return pack_string(address) + pack_string(''.join(types)) + b''.join(data)


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


def send(dest, address, *args):
    with Client(dest) as client:
        client.send(address, *args)
