# -*- coding: utf-8 -*-
"""OSC message parsing and building functions."""

try:
    from time import time
except ImportError:
    from utime import time

from struct import pack

try:
    const
except:
    const = lambda x: x

# UNIX_EPOCH = datetime.date(*time.gmtime(0)[0:3])
# NTP_EPOCH = datetime.date(1900, 1, 1)
# NTP_DELTA = (UNIX_EPOCH - NTP_EPOCH).days * 24 * 3600
NTP_DELTA = const(2208988800)
ISIZE = const(4294967296)  # 2**32


class Impulse:
    pass


class Bundle:
    """Container for an OSC bundle."""

    def __init__(self, timetag=None, *items):
        """Create bundle from given OSC timetag and messages/sub-bundles.

        timetag, if given, must be in float seconds since the NTP epoch
        (1990-01-01 00:00). It defaults to the current time.

        Pass in messages or bundles via positional arguments as binary data
        (bytes as returned by ``create_message`` resp. ``Bundle.pack``) or as
        ``Bundle`` instance or (address, *args) tuples.

        """
        self.timetag = time() + NTP_DELTA if timetag is None else timetag
        self._items = list(items)

    def add(self, *items):
        self._items.extend(list(items))

    def __iter__(self):
        return iter(self._items)


def to_frac(t):
    """Return seconds and fractional part of NTP timestamp as 2-item tuple."""
    sec = int(t)
    return sec, int(abs(t - sec) * ISIZE)


def to_time(sec, frac):
    """Return NTP timestamp from integer seconds and fractional part."""
    return sec + float(frac) / ISIZE
