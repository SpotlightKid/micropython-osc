CircuitPython-OSC
===============

circuitpython-osc (aka `uosc`) is a minimal [Open Sound Control] \(OSC) client
and server library for [MicroPython], [CircuitPython] and CPython 2 or 3.

This fork changes the 7 lines required to support CircuitPython.  
Upstream refused to support it despite the work being done for them.  
This fork will remain up-to-date with upstream.


Status / Supported Boards
-------------------------

It should work on the Unix, stm32 (Pyboard) and esp8266 port of MicroPython
and under CPython 2.7 and 3.3+. Since OSC is a protocol commonly using an IP
network and UDP or TCP packets as a transport, the main requirement is a
working and compatible `socket` module. Currently this module only supports UDP
as the transport.

The server code so far has only been tested under the Unix port and CPython 2
and 3, but the client portion has been confirmed to work on a ESP-8266 board
running MicroPython 1.8.x.


Usage
-----

Here's a minmal usage example for the client. Further documentation is
currently only available by looking at the docstrings and the source code (the
whole package has a total LLOC of < 400).

    from uosc.client import Bundle, Client, create_message

    osc = Client('192.168.4.2', 9001)
    osc.send('/controls/frobnicator', 42, 3.1419, "spamm")
    b = Bundle()
    b.add(create_message("/foo", bar))
    b.add(create_message("/spamm", 12345))
    osc.send(b)


Examples
--------

The [examples](./examples) directory contains some simple example scripts using
this library to implement special OSC clients or simple OSC UDP servers.

To use the server examples with the unix port of MicroPython, the following 
required modules from the [micropython-lib] are included in this directory:

* argparse
* ffilib

Either use the provided shell wrappers to run the server examples or install
these two modules to `~/.micropython/lib`.


[Open Sound Control]: http://opensoundcontrol.org
[MicroPython]: http://micropython.org
[micropython-lib]: https://github.com/micropython/micropython-lib
[CircuitPython]: https://circuitpython.org
