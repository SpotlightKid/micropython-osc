#!/bin/bash

export MICROPYPATH="$(pwd):$MICROPYPATH"
exec micropython uosc/__main__.py "$@"
