#!/usr/bin/env -S uv run --script
import os
from parallelism import pmap

def burn(x):
    while True:
        pass

try:
    pmap(burn, range((os.cpu_count() or 2) - 1), max_workers=(os.cpu_count() or 2) - 1)
except KeyboardInterrupt:
    pass
