from utime import time
from ustruct import pack


# UNIX_EPOCH = datetime.date(*time.gmtime(0)[0:3])
# NTP_EPOCH = datetime.date(1900, 1, 1)
# NTP_DELTA = (UNIX_EPOCH - NTP_EPOCH).days * 24 * 3600
NTP_DELTA = const(2208988800)
ISIZE = const(4294967296)  # 2**32
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


class Bundle(list):
    """Container for an OSC bundle (subclasses list)."""

    def __init__(self, timetag=None, *msgs):
        """Create bundle from given OSC timetag and messages/sub-bundles.

        timetag, if given, must be in float seconds since the NTP epoch
        (1990-01-01 00:00). It defaults to the current time.

        Pass in messages or bundles via positional arguments as binary data
        (bytes as returned by ``create_message`` resp. ``Bundle.pack``) or as
        ``Bundle`` instance or (address, *args) tuples.

        """
        self.timetag = time() + NTP_EPOCH if timetag is None else timetag
        super(Bundle, self).__init__(msgs)

    def pack(self):
        """Return bundle data packed into a binary string."""
        data = []
        for msg in self:
            if isinstance(msg, Bundle):
                msg = Bundle.pack()
            elif isinstance(msg, tuple):
                msg = creat_message(*msg)

            data.append(pack('>I', len(msg)) + msg)

        return b'#bundle\0' + pack_timetag(self.timetag) + b''.join(data)


def to_frac(t):
    """Return seconds and fractional part of NTP timestamp as 2-item tuple."""
    sec = int(t)
    return sec, int(abs(t - sec) * ISIZE)


def to_time(sec, frac):
    """Return NTP timestamp from integer seconds and fractional part."""
    return sec + float(frac) / ISIZE


def pack_timetag(t):
    """Pack an OSC timetag into 64-bit binary blob."""
    return pack('>II', *to_frac(t))


def pack_string(s):
    """Pack a string into a binary OSC string."""
    s = s.encode('ascii', 'strict') + b'\0'
    if len(s) % 4:
        s += b'\0' * (4 - len(s) % 4)
    return s


def pack_blob(b):
    """Pack a bytes, bytearray or tuple/list of ints into a binary OSC blob."""
    if isinstance(b, (tuple, list)):
        b = bytearray(b)
    b = bytes(pack('>I', len(b)) + b)
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
    data = []
    types = [',']

    for arg in args:
        type_ = type(arg)

        if isinstance(arg, tuple):
            typetag, arg = arg
        else:
            typetag = TYPE_MAP.get(type_) or TYPE_MAP.get(arg)

        if typetag in 'ihfd':
            data.append(pack('>' + typetag, arg))
        elif typetag in 'sS':
            data.append(pack_string(arg))
        elif typetag in 'brm':
            data.append(pack_blob(arg))
        elif typetag == 'c':
            data.append(pack('>I', ord(arg)))
        elif typetag == 't':
            data.append(pack_timetag(arg))
        elif typetag not in 'IFNT':
            raise TypeError("Argument of type '%s' not supported." % type_)

        types.append(typetag)

    return pack_string(address) + pack_string(''.join(types)) + b''.join(data)
