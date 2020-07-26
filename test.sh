#!/bin/bash

pyflakes $(find -name '*.py') &&
exec pytest "$@" typesetting/tests/tests.py
