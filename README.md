# Micropython-OSC

Micropython-osc (aka `uosc`) is a minimal [Open Sound Control] \(OSC) client
and server library for [MicroPython] and CPython.


## Status / Supported Boards

It should work on the Unix, stm32 (Pyboard) and esp8266 port of MicroPython
and under CPython 3.8+. Since OSC is a protocol commonly using an IP network
and UDP or TCP packets as a transport, the main requirement is a working and
compatible `socket` module. Currently this module only supports UDP as the
transport.

The server code so far has only been tested under the Unix port and CPython,
but the client portion has been confirmed to work on a ESP-8266 board running
MicroPython 1.8.x.


## Usage

Here's a minmal usage example for the client. Further documentation is
currently only available by looking at the docstrings and the source code.

    from uosc.client import Bundle, Client, create_message

    osc = Client('192.168.4.2', 9001)
    osc.send('/controls/frobnicator', 42, 3.1419, "spamm")
    b = Bundle()
    b.add(create_message("/foo", bar))
    b.add(create_message("/spamm", 12345))
    osc.send(b)


## Examples

The [examples](./examples) directory contains some simple example scripts using
this library to implement special OSC clients or simple OSC UDP servers.

To use the server examples with the unix port of MicroPython, the following
required modules from the [micropython-lib] are included in this directory:

* argparse
* ffilib

Either use the provided shell wrappers to run the server examples or install
these two modules to `~/.micropython/lib`.


## License

`micropython-osc` is Free and Open Source software and released under the MIT
license. For details see the file [LICENSE.md](./LICENSE.md).


## Author

`micropython-osc` is written by *Christopher Arndt* and was started in 2015.


[Open Sound Control]: http://opensoundcontrol.org
[MicroPython]: http://micropython.org
[micropython-lib]: https://github.com/micropython/micropython-lib
