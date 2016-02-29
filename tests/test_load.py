#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from uosc.client import Client


def run_loadtest(c):
    nreq = 0
    s = time.time()
    while True:
        nreq += 1
        c.send('/foo', 42, 23)
        e = time.time()
        if e - s > 5.0:
            print("{} req/s".format(nreq/5.0))
            nreq = 0
            s = time.time()

if __name__ == '__main__':
    c = Client(9001)
    try:
        run_loadtest(c)
    except KeyboardInterrupt:
        pass

