#!/usr/bin/env bash

if [[ -d build ]]; then
    rm -rd build || exit 1
fi
if [[ -d dist ]]; then
    rm -rd dist || exit 1
fi
if [[ ! -d .venv ]]; then
    python3 -m venv .venv || exit 1
fi
source .venv/bin/activate || exit 1
python -m pip install build || exit 1
python -m build || exit 1
