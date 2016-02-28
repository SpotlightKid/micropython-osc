#!/bin/bash

export MICROPYPATH="$(pwd):$MICROPYPATH"
exec micropython examples/async_server.py "$@"
