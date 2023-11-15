#!/bin/bash

export MICROPYPATH="$(pwd):$(pwd)/examples:${MICROPYPATH:-.frozen:$HOME/.micropython/lib:/usr/lib/micropython}"
exec micropython uosc/tools/async_server.py "$@"
