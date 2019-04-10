# -*- coding: utf-8 -*-
"""OSC message parsing and building functions."""

try:
    from time import time
except ImportError:
    from utime import time

try:
    from micropython import const
except ImportError:
    const = lambda x: x  # noqa:E731


# UNIX_EPOCH = datetime.date(*time.gmtime(0)[0:3])
# NTP_EPOCH = datetime.date(1900, 1, 1)
# NTP_DELTA = (UNIX_EPOCH - NTP_EPOCH).days * 24 * 3600
NTP_DELTA = 2208988800
ISIZE = 4294967296  # 2**32


class Impulse:
    pass


class Bundle:
    """Container for an OSC bundle."""

    def __init__(self, *items):
        """Create bundle from given OSC timetag and messages/sub-bundles.

        An OSC timetag can be given as the first positional argument, and must
        be an int or float of seconds since the NTP epoch (1990-01-01 00:00).
        It defaults to the current time.

        Pass in messages or bundles via positional arguments as binary data
        (bytes as returned by ``create_message`` resp. ``Bundle.pack``) or as
        ``Bundle`` instances or (address, *args) tuples.

        """
        if items and isinstance(items[0], (int, float)):
            self.timetag = items[0]
            items = items[1:]
        else:
            self.timetag = time() + NTP_DELTA

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
