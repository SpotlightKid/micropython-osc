# -*- coding: utf-8 -*-
#
#  uosc/server.py
#
"""A minimal OSC UDP server."""

import logging
import socket

try:
    from ustruct import unpack
except ImportError:
    from struct import unpack

from uosc.common import Impulse, to_time

if __debug__:
    from uosc.socketutil import get_hostport


log = logging.getLogger("uosc.server")
MAX_DGRAM_SIZE = 1472


def split_oscstr(msg, offset):
    end = msg.find(b'\0', offset)
    return msg[offset:end].decode('utf-8'), (end + 4) & ~0x03


def split_oscblob(msg, offset):
    start = offset + 4
    size = unpack('>I', msg[offset:start])[0]
    return msg[start:start + size], (start + size + 4) & ~0x03


def parse_timetag(msg, offset):
    """Parse an OSC timetag from msg at offset."""
    return to_time(unpack('>II', msg[offset:offset + 4]))


def parse_message(msg, strict=False):
    args = []
    addr, ofs = split_oscstr(msg, 0)

    if not addr.startswith('/'):
        raise ValueError("OSC address pattern must start with a slash.")

    # type tag string must start with comma (ASCII 44)
    if ofs < len(msg) and msg[ofs:ofs + 1] == b',':
        tags, ofs = split_oscstr(msg, ofs)
        tags = tags[1:]
    else:
        errmsg = "Missing/invalid OSC type tag string."
        if strict:
            raise ValueError(errmsg)
        else:
            log.warning(errmsg + ' Ignoring arguments.')
            tags = ''

    for typetag in tags:
        size = 0

        if typetag in 'ifd':
            size = 8 if typetag == 'd' else 4
            args.append(unpack('>' + typetag, msg[ofs:ofs + size])[0])
        elif typetag in 'sS':
            s, ofs = split_oscstr(msg, ofs)
            args.append(s)
        elif typetag == 'b':
            s, ofs = split_oscblob(msg, ofs)
            args.append(s)
        elif typetag in 'rm':
            size = 4
            args.append(unpack('BBBB', msg[ofs:ofs + size]))
        elif typetag == 'c':
            size = 4
            args.append(chr(unpack('>I', msg[ofs:ofs + size])[0]))
        elif typetag == 'h':
            size = 8
            args.append(unpack('>q', msg[ofs:ofs + size])[0])
        elif typetag == 't':
            size = 8
            args.append(parse_timetag(msg, ofs))
        elif typetag in 'TFNI':
            args.append({'T': True, 'F': False, 'I': Impulse}.get(typetag))
        else:
            raise ValueError("Type tag '%s' not supported." % typetag)

        ofs += size

    return (addr, tags, tuple(args))


def parse_bundle(bundle, strict=False):
    """Parse a binary OSC bundle.

    Returns a generator which walks over all contained messages and bundles
    recursively, depth-first. Each item yielded is a (timetag, message) tuple.

    """
    if not bundle.startswith(b'#bundle\0'):
        raise TypeError("Bundle must start with b'#bundle\\0'.")

    ofs = 16
    timetag = to_time(*unpack('>II', bundle[8:ofs]))

    while True:
        if ofs >= len(bundle):
            break

        size = unpack('>I', bundle[ofs:ofs + 4])[0]
        element = bundle[ofs + 4:ofs + 4 + size]
        ofs += size + 4

        if element.startswith(b'#bundle'):
            for el in parse_bundle(element):
                yield el
        else:
            yield timetag, parse_message(element, strict)


def handle_osc(data, src, dispatch=None, strict=False):
    try:
        head, _ = split_oscstr(data, 0)

        if head.startswith('/'):
            messages = [(-1, parse_message(data, strict))]
        elif head == '#bundle':
            messages = parse_bundle(data, strict)
    except Exception as exc:
        if __debug__:
            log.debug("Could not parse message from %s:%i: %s",
                      *get_hostport(src), exc)
            log.debug("Data: %r", data)
        return

    try:
        for timetag, (oscaddr, tags, args) in messages:
            if __debug__:
                log.debug("OSC address: %s" % oscaddr)
                log.debug("OSC type tags: %r" % tags)
                log.debug("OSC arguments: %r" % (args,))

            if dispatch:
                dispatch(timetag, (oscaddr, tags, args, src))
    except Exception as exc:
        log.error("Exception in OSC handler: %s", exc)


def run_server(saddr, port, handler=handle_osc):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if __debug__: log.debug("Created OSC UDP server socket.")

    sock.bind((saddr, port))
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
