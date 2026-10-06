"""Run an engine version in-process with diagnostics, for chasing hangs in matches.

python match/engine_host.py <engine dir> <log file>

Same engine code and speed as `python <engine dir>/chess_engine.py`, but stderr
(including exceptions in the search thread) goes to the log file, and if no
input line arrives for HANG_SECONDS, every thread's stack is dumped to the log.
"""

import faulthandler
import os
import sys
import time

HANG_SECONDS = 8

path, log_path = os.path.abspath(sys.argv[1]), sys.argv[2]
log = open(log_path, "a", buffering=1)
sys.stderr = log
faulthandler.enable(file=log)
sys.path.insert(0, path)
os.chdir(path)


class RearmingStdin:
    """Iterates stdin lines, re-arming the stack-dump timer on each one."""

    def __init__(self, stream):
        self.stream = stream

    def __iter__(self):
        for line in self.stream:
            faulthandler.cancel_dump_traceback_later()
            faulthandler.dump_traceback_later(HANG_SECONDS, file=log)
            self.last = (time.strftime("%H:%M:%S"), line.strip())
            if line.startswith("go"):
                log.write("%s pid %d: %s\n" % (time.strftime("%H:%M:%S"), os.getpid(), line.strip()))
            yield line


sys.stdin = RearmingStdin(sys.stdin)
from engine.uci import main  # noqa: E402

main()
