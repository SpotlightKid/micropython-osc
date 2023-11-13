# -*- coding: utf-8 -*-
#
#  uosc/common.py
#
"""OSC message parsing and building functions."""

try:
    from time import time
except ImportError:
    from utime import time


# UNIX_EPOCH = datetime.datetime.utcfromtimestamp(0)
# NTP_EPOCH = datetime.datetime(1900, 1, 1, 0, 0, 0)
# NTP_DELTA = int((UNIX_EPOCH - NTP_EPOCH).total_seconds())
NTP_DELTA = 2208988800
ISIZE = 4294967296  # 2**32

TimetagNow = object()

Impulse = object()


class Bundle:
    """Container for an OSC bundle."""

    def __init__(self, *items):
        """Create bundle from given OSC timetag and messages and sub-bundles.

        An OSC timetag can be given as the first positional argument, and must
        be an int or float of seconds since the NTP epoch (1990-01-01 00:00) or
        the ``uosc.common.TimetagNow`` constant. It defaults to the current
        time.

        Pass in messages or bundles via positional arguments as binary data
        (bytes as returned by ``create_message`` resp. ``Bundle.pack``) or as
        ``Bundle`` instances or ``(oscaddress, *args)`` tuples.

        """
        if items and (isinstance(items[0], (int, float)) or items[0] is TimetagNow):
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
