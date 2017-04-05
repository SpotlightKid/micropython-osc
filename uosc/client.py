# -*- coding: utf-8 -*-
"""Simple OSC client."""

import socket

try:
    from ustruct import pack
except ImportError:
    from struct import pack

from uosc.common import Bundle, to_frac


if isinstance('', bytes):
    have_bytes = False
    unicodetype = unicode  # noqa
else:
    have_bytes = True
    unicodetype = str

TYPE_MAP = {
    int: 'i',
    float: 'f',
    bytes: 'b',
    bytearray: 'b',
    unicodetype: 's',
    True: 'T',
    False: 'F',
    None: 'N',
}


def pack_addr(addr):
    """Pack a (host, port) tuple into the format expected by socket methods."""
    if isinstance(addr, (bytes, bytearray)):
        return addr

    if len(addr) != 2:
        raise NotImplementedError("Only IPv4/v6 supported")

    addrinfo = socket.getaddrinfo(addr[0], addr[1])
    return addrinfo[0][4]


def pack_timetag(t):
    """Pack an OSC timetag into 64-bit binary blob."""
    return pack('>II', *to_frac(t))


def pack_string(s, encoding='utf-8'):
    """Pack a string into a binary OSC string."""
    if isinstance(s, unicodetype):
        s = s.encode(encoding)
    assert all((i if have_bytes else ord(i)) < 128 for i in s), (
        "OSC strings may only contain ASCII chars.")

    slen = len(s)
    return s + b'\0' * (((slen + 4) & ~0x03) - slen)


def pack_blob(b, encoding='utf-8'):
    """Pack a bytes, bytearray or tuple/list of ints into a binary OSC blob."""
    if isinstance(b, (tuple, list)):
        b = bytearray(b)
    elif isinstance(b, unicodetype):
        b = b.encode(encoding)

    blen = len(b)
    b = pack('>I', blen) + bytes(b)
    return b + b'\0' * (((blen + 3) & ~0x03) - blen)


def pack_bundle(bundle):
    """Return bundle data packed into a binary string."""
    data = []
    for msg in bundle:
        if isinstance(msg, Bundle):
            msg = pack_bundle(msg)
        elif isinstance(msg, tuple):
            msg = create_message(*msg)

        data.append(pack('>I', len(msg)) + msg)

    return b'#bundle\0' + pack_timetag(bundle.timetag) + b''.join(data)


def pack_midi(val):
    assert not isinstance(val, unicodetype), (
        "Value with tag 'm' or 'r' must be bytes, bytearray or a sequence of "
        "ints, not %s" % unicodetype)
    if not have_bytes and isinstance(val, str):
        val = (ord(c) for c in val)

    return pack('BBBB', *tuple(val))


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
            data.append(pack_midi(arg))
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
    def __init__(self, host, port=None):
        if port is None:
            if isinstance(host, (list, tuple)):
                host, port = host
            else:
                port = host
                host = '127.0.0.1'

        self.dest = pack_addr((host, port))
        self.sock = None

    def send(self, msg, *args, **kw):
        dest = pack_addr(kw.get('dest', self.dest))

        if not self.sock:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if isinstance(msg, Bundle):
            msg = pack_bundle(msg)
        elif args or isinstance(msg, unicodetype):
            msg = create_message(msg, *args)

        self.sock.sendto(msg, dest)

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def send(dest, address, *args):
    with Client(dest) as client:
        client.send(address, *args)
