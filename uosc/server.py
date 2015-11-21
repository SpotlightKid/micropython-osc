#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  uosc/server.py
#
"""A minimal OSC UDP server."""

import logging
import socket

from uosc.common import parse_message
from uosc.socketutil import get_hostport


log = logging.getLogger("uosc.server")
MAX_DGRAM_SIZE = 1472


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
