# -*- coding: utf-8 -*-
#
#  uosc/server.py
#
"""A minimal OSC UDP server."""

import logging
import socket

from struct import unpack

from uosc.common import Impulse, to_time
from uosc.socketutil import get_hostport


log = logging.getLogger("uosc.server")
MAX_DGRAM_SIZE = 1472


def split_oscstr(msg, offset):
    end = msg.find(b'\0', offset)
    return msg[offset:end].decode('utf-8'), (end + 4) & ~0x03


def split_oscblob(msg, offset):
    start = offset + 4
    size = unpack('>I', msg[offset:start])[0]
    return msg[start:start+size], (start + size + 4) & ~0x03


def parse_timetag(msg, offset):
    """Parse an OSC timetag from msg at offset."""
    return to_time(unpack('>II', msg[offset:offset+4]))


def parse_message(msg):
    args = []
    addr, ofs = split_oscstr(msg, 0)

    if not addr.startswith('/'):
        raise ValueError("OSC address pattern must start with a slash.")

    # type tag string must start with comma (ASCII 44)
    if ofs < len(msg) and msg[ofs] == 44:
        tags, ofs = split_oscstr(msg, ofs)
        tags = tags[1:]
    else:
        log.warning("Missing/invalid OSC type tag string. Ignoring arguments.")
        tags = ''

    for typetag in tags:
        size = 0

        if typetag in 'ifd':
            size = 8 if typetag == 'd' else 4
            args.append(unpack('>' + typetag, msg[ofs:ofs+size])[0])
        elif typetag in 'sS':
            s, ofs = split_oscstr(msg, ofs)
            args.append(s)
        elif typetag == 'b':
            s, ofs = split_oscblob(msg, ofs)
            args.append(s)
        elif typetag in 'rm':
            size = 4
            args.append(unpack('BBBB', msg[ofs:ofs+size]))
        elif typetag == 'c':
            size = 4
            args.append(chr(unpack('>I', msg[ofs:ofs+size])[0]))
        elif typetag == 'h':
            size = 8
            args.append(unpack('>q', msg[ofs:ofs+size])[0])
        elif typetag == 't':
            size = 8
            args.append(parse_timetag(msg, offset))
        elif typetag in 'TFNI':
            args.append({'T': True, 'F': False, 'I': Impulse}.get(typetag))
        else:
            raise ValueError("Type tag '%s' not supported." % typetag)

        ofs += size

    return (addr, tags, tuple(args))


def parse_bundle(bundle):
    """Parse a binary OSC bundle.

    Returns a generator which walks over all contained messages and bundles
    recursively, depth-first. Each item yielded is a (timetag, message) tuple.

    """
    if not bundle.startswith(b'#bundle\0'):
        raise TypeError("Bundle must start with '#bundle\\0'.")

    ofs = 16
    timetag = to_time(*unpack('>II', bundle[8:ofs]))

    while True:
        if ofs >= len(bundle):
            break

        size = unpack('>I', bundle[ofs:ofs+4])[0]
        element = bundle[ofs+4:ofs+4+size]
        ofs += size + 4

        if element.startswith('#bundle'):
            for el in parse_bundle(element):
                yield el
        else:
            yield timetag, parse_message(element)


def handle_osc(addr, tags, args, src):
    log.debug("OSC address: %s" % addr)
    log.debug("OSC type tags: %r" % tags)
    log.debug("OSC arguments: %r" % (args,))
    pass


def run_server(saddr, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    log.debug("Created OSC UDP server socket.")
    sock.bind((saddr, port))
    log.debug("Bound socket to port %i on %s.", port, saddr)

    try:
        log.debug("Entering receive loop...")
        while True:
            data, caddr = sock.recvfrom(MAX_DGRAM_SIZE)

            if isinstance(caddr, bytes):
                caddr = get_hostport(caddr)

            log.debug("RECV %i bytes from %s:%s", len(data), *caddr)

            try:
                oscaddr, tags, args = parse_message(data)
            except:
                log.debug("Could not parse message from %s:%i.", *caddr)
                log.debug("Data: %r", data)
                continue

            try:
                handle_osc(oscaddr, tags, args, caddr)
            except Exception as exc:
                log.error("Exception in OSC handler: %s", exc)
    finally:
        sock.close()
        log.info("Bye!")
