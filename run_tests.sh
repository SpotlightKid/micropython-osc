#!/bin/bash

export MICROPYPATH="$(pwd):$MICROPYPATH"
micropython tests/test_client.py "$@" && \
micropython tests/test_server.py "$@"
