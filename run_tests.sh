#!/bin/bash

export MICROPYPATH="$(pwd):${MICROPYPATH:-.frozen:$HOME/.micropython/lib:/usr/lib/micropython}"
micropython tests/test_client.py "$@" && \
micropython tests/test_server.py "$@"
