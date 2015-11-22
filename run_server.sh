#!/bin/bash

export MICROPYPATH="$(pwd):$MICROPYPATH"
micropython uosc/__main__.py "$@"
