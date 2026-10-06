"""Test fixture: a UCI 'engine' that handshakes but never answers go, to simulate a stalled engine."""

import sys

for line in sys.stdin:
    cmd = line.split()[:1]
    if cmd == ["uci"]:
        print("uciok", flush=True)
    elif cmd == ["isready"]:
        print("readyok", flush=True)
    elif cmd == ["quit"]:
        break
