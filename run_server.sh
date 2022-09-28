#!/bin/bash

export MICROPYPATH="$(pwd):${MICROPYPATH:-.frozen:$HOME/.micropython/lib:/usr/lib/micropython}"
exec micropython examples/minimal_server.py "$@"
