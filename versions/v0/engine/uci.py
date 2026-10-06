"""UCI protocol loop. The search runs in a worker thread so `stop` and `quit` are answered."""

import sys
import threading

from engine.board import Board, move_uci
from engine.search import Searcher

NAME = "PyThistle"
AUTHOR = "Emma Leonhart and Claude"


def time_budget(tokens, side_white):
    """Seconds to spend on this move from the `go` arguments, or None for no limit."""
    args = {}
    i = 0
    while i < len(tokens):
        key = tokens[i]
        if key in ("infinite", "ponder"):
            args[key] = True
            i += 1
        elif i + 1 < len(tokens):
            args[key] = tokens[i + 1]
            i += 2
        else:
            i += 1
    if "movetime" in args:
        # Leave a little for process and pipe overhead.
        return max(0.01, int(args["movetime"]) / 1000.0 - 0.05), None
    depth = int(args["depth"]) if "depth" in args else None
    left_key, inc_key = ("wtime", "winc") if side_white else ("btime", "binc")
    if left_key in args:
        left = int(args[left_key]) / 1000.0
        inc = int(args.get(inc_key, 0)) / 1000.0
        moves_to_go = int(args.get("movestogo", 30))
        budget = left / max(moves_to_go, 1) + inc * 0.8
        return max(0.01, min(budget, left * 0.5)), depth
    return None, depth


class UCI:
    def __init__(self, out=sys.stdout):
        self.board = Board()
        self.searcher = Searcher()
        self.out = out
        self.thread = None

    def send(self, line):
        self.out.write(line + "\n")
        self.out.flush()

    def wait(self):
        if self.thread is not None:
            self.thread.join()
            self.thread = None

    def stop(self):
        if self.thread is not None:
            self.searcher.stop = True
            self.wait()

    def handle(self, line):
        tokens = line.split()
        if not tokens:
            return True
        cmd = tokens[0]
        if cmd == "uci":
            self.send("id name " + NAME)
            self.send("id author " + AUTHOR)
            self.send("uciok")
        elif cmd == "isready":
            self.send("readyok")
        elif cmd == "ucinewgame":
            self.stop()
            self.searcher.new_game()
        elif cmd == "position":
            self.stop()
            self.position(tokens[1:])
        elif cmd == "go":
            self.stop()
            movetime, depth = time_budget(tokens[1:], self.board.side == 1)
            board = self.board
            self.thread = threading.Thread(target=self.go, args=(board, movetime, depth or 64), daemon=True)
            self.thread.start()
        elif cmd == "stop":
            self.stop()
        elif cmd == "quit":
            self.stop()
            return False
        elif cmd == "d":
            self.send(self.board.fen())
        return True

    def position(self, tokens):
        if not tokens:
            return
        if tokens[0] == "startpos":
            self.board = Board()
            rest = tokens[1:]
        elif tokens[0] == "fen":
            if "moves" in tokens:
                i = tokens.index("moves")
                fen = " ".join(tokens[1:i])
                rest = tokens[i:]
            else:
                fen = " ".join(tokens[1:])
                rest = []
            self.board = Board(fen)
        else:
            return
        if rest and rest[0] == "moves":
            for s in rest[1:]:
                m = self.board.parse_uci(s)
                if m is None:
                    break
                self.board.make(m)

    def go(self, board, movetime, depth):
        best = self.searcher.search(board, movetime=movetime, max_depth=depth, info=self.send)
        self.send("bestmove " + (move_uci(best) if best else "0000"))


def main():
    uci = UCI()
    for line in sys.stdin:
        if not uci.handle(line.strip()):
            break
    uci.wait()
