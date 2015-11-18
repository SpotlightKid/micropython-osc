#!/bin/bash

export MICROPYPATH="$(pwd):$MICROPYPATH"
exec micropython tests/test_common.py "$@"
