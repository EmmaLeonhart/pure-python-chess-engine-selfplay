"""Play a match between two engine versions over UCI and report score and Elo.

Usage:
    python match/run_match.py --a versions/v1 --b versions/v0 --name round01

Each engine path is a directory containing chess_engine.py. Every opening in
match/openings.txt is played twice, once with each engine as white. Results go
to matches/<name>/: games.pgn, summary.json (rewritten after every game, so an
interrupted match keeps what it finished) and log.txt.
"""

import argparse
import datetime
import json
import os
import queue
import subprocess
import sys
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from engine.board import Board  # noqa: E402
from match.stats import match_stats, format_stats  # noqa: E402

RESIGN_CP = 1000
RESIGN_PLIES = 8      # 4 consecutive moves by each engine
MAX_PLIES = 300
MATE_SCORE = 100_000


def load_openings(path=os.path.join(ROOT, "match", "openings.txt")):
    out = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            name, moves = (x.strip() for x in line.split("|"))
            out.append((name, moves.split()))
    return out


class EngineError(Exception):
    pass


class Engine:
    def __init__(self, path):
        self.path = path
        self.proc = subprocess.Popen(
            [sys.executable, os.path.join(path, "chess_engine.py")],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, bufsize=1, cwd=path)
        self.lines = queue.Queue()
        threading.Thread(target=self._reader, daemon=True).start()
        self.send("uci")
        self.wait_for("uciok", 30)

    def _reader(self):
        for line in self.proc.stdout:
            self.lines.put(line.strip())
        self.lines.put(None)

    def send(self, s):
        try:
            self.proc.stdin.write(s + "\n")
            self.proc.stdin.flush()
        except OSError as e:
            raise EngineError("write failed: %s" % e)

    def wait_for(self, prefix, timeout):
        """Read lines until one starts with prefix; return (that line, all lines read)."""
        deadline = time.monotonic() + timeout
        seen = []
        while True:
            left = deadline - time.monotonic()
            if left <= 0:
                raise EngineError("timeout waiting for %r" % prefix)
            try:
                line = self.lines.get(timeout=left)
            except queue.Empty:
                raise EngineError("timeout waiting for %r" % prefix)
            if line is None:
                raise EngineError("engine exited")
            seen.append(line)
            if line.startswith(prefix):
                return line, seen

    def new_game(self):
        self.send("ucinewgame")
        self.send("isready")
        self.wait_for("readyok", 30)

    def go(self, moves, movetime_ms):
        self.send("position startpos" + (" moves " + " ".join(moves) if moves else ""))
        self.send("go movetime %d" % movetime_ms)
        line, seen = self.wait_for("bestmove", movetime_ms / 1000.0 + 10)
        score = None
        for l in seen:
            parts = l.split()
            if "score" in parts:
                i = parts.index("score")
                if parts[i + 1] == "cp":
                    score = int(parts[i + 2])
                elif parts[i + 1] == "mate":
                    mate = int(parts[i + 2])
                    score = MATE_SCORE if mate > 0 else -MATE_SCORE
        return line.split()[1], score

    def quit(self):
        try:
            self.send("quit")
            self.proc.wait(timeout=5)
        except Exception:
            self.proc.kill()
        for f in (self.proc.stdin, self.proc.stdout):
            try:
                f.close()
            except Exception:
                pass


def play_game(white, black, opening, movetime_ms):
    """Play one game. Returns (result, termination, moves) with result '1-0', '0-1' or '1/2-1/2'."""
    board = Board()
    moves = []
    for s in opening:
        board.make(board.parse_uci(s))
        moves.append(s)
    white.new_game()
    black.new_game()
    white_pov = []  # each engine's reported score, converted to white's point of view
    while True:
        legal = board.legal_moves()
        if not legal:
            if board.in_check():
                return ("0-1" if board.side == 1 else "1-0"), "checkmate", moves
            return "1/2-1/2", "stalemate", moves
        if board.halfmove >= 100:
            return "1/2-1/2", "fifty-move rule", moves
        if board.is_repetition(count=2):
            return "1/2-1/2", "threefold repetition", moves
        if board.insufficient_material():
            return "1/2-1/2", "insufficient material", moves
        if len(moves) >= MAX_PLIES:
            return "1/2-1/2", "adjudicated: move limit", moves
        recent = white_pov[-RESIGN_PLIES:]
        if len(recent) == RESIGN_PLIES and all(s is not None for s in recent):
            if all(s >= RESIGN_CP for s in recent):
                return "1-0", "adjudicated: resignation", moves
            if all(s <= -RESIGN_CP for s in recent):
                return "0-1", "adjudicated: resignation", moves

        mover = white if board.side == 1 else black
        loser_result = "0-1" if board.side == 1 else "1-0"
        try:
            uci, score = mover.go(moves, movetime_ms)
        except EngineError as e:
            return loser_result, "forfeit: %s" % e, moves
        m = board.parse_uci(uci)
        if m is None:
            return loser_result, "forfeit: illegal move %s" % uci, moves
        white_pov.append(None if score is None else score * board.side)
        board.make(m)
        moves.append(uci)


def pgn(game):
    board = Board()
    tokens = []
    for i, s in enumerate(game["moves"]):
        if i % 2 == 0:
            tokens.append("%d." % (i // 2 + 1))
        tokens.append(s)
        board.make(board.parse_uci(s))
    tokens.append(game["result"])
    headers = [
        ("Event", game["match"]), ("Round", str(game["index"] + 1)),
        ("White", game["white"]), ("Black", game["black"]),
        ("Result", game["result"]), ("Opening", game["opening"]),
        ("Termination", game["termination"]),
        ("TimeControl", "movetime %d ms" % game["movetime_ms"]),
    ]
    lines = ['[%s "%s"]' % h for h in headers]
    # Long-algebraic (UCI) movetext keeps this standard-library-only; most PGN readers accept it.
    body, line = [], ""
    for t in tokens:
        if len(line) + len(t) + 1 > 79:
            body.append(line)
            line = t
        else:
            line = (line + " " + t).strip()
    body.append(line)
    return "\n".join(lines) + "\n\n" + "\n".join(body) + "\n\n"


def run_match(a, b, name, movetime_ms=1000, workers=None, max_games=None, out_root=None):
    openings = load_openings()
    jobs = []
    for i, (oname, omoves) in enumerate(openings):
        jobs.append((2 * i, oname, omoves, True))       # A plays white
        jobs.append((2 * i + 1, oname, omoves, False))  # A plays black
    if max_games is not None:
        jobs = jobs[:max_games]
    workers = workers or max(1, (os.cpu_count() or 2) // 2)
    out_dir = os.path.join(out_root or os.path.join(ROOT, "matches"), name)
    os.makedirs(out_dir, exist_ok=True)
    a_label, b_label = os.path.basename(os.path.normpath(a)), os.path.basename(os.path.normpath(b))
    if a_label == b_label:
        a_label, b_label = a_label + "-A", b_label + "-B"

    job_q = queue.Queue()
    for j in jobs:
        job_q.put(j)
    games = []
    lock = threading.Lock()
    started = datetime.datetime.now().astimezone()
    log = open(os.path.join(out_dir, "log.txt"), "a")

    def write_summary(final=False):
        w = sum(1 for g in games if g["a_score"] == 1)
        d = sum(1 for g in games if g["a_score"] == 0.5)
        l = sum(1 for g in games if g["a_score"] == 0)
        summary = {
            "match": name, "a": a, "b": b, "a_label": a_label, "b_label": b_label,
            "movetime_ms": movetime_ms, "workers": workers, "planned_games": len(jobs),
            "started": started.isoformat(timespec="seconds"),
            "finished": datetime.datetime.now().astimezone().isoformat(timespec="seconds") if final else None,
            "stats": match_stats(w, d, l) if games else None,
            "games": sorted(({k: v for k, v in g.items() if k != "moves"} for g in games),
                            key=lambda g: g["index"]),
        }
        with open(os.path.join(out_dir, "summary.json"), "w") as f:
            json.dump(summary, f, indent=1)
        return summary

    def worker():
        ea, eb = Engine(a), Engine(b)
        try:
            while True:
                try:
                    index, oname, omoves, a_white = job_q.get_nowait()
                except queue.Empty:
                    return
                white, black = (ea, eb) if a_white else (eb, ea)
                result, term, moves = play_game(white, black, omoves, movetime_ms)
                a_score = {"1-0": 1.0, "0-1": 0.0, "1/2-1/2": 0.5}[result]
                if not a_white:
                    a_score = 1.0 - a_score
                game = {"match": name, "index": index, "opening": oname,
                        "white": a_label if a_white else b_label, "black": b_label if a_white else a_label,
                        "result": result, "termination": term, "plies": len(moves),
                        "a_score": a_score, "movetime_ms": movetime_ms, "moves": moves}
                with lock:
                    games.append(game)
                    with open(os.path.join(out_dir, "games.pgn"), "a") as f:
                        f.write(pgn(game))
                    summary = write_summary()
                    line = "[%s] game %d/%d %s: %s vs %s %s (%s); %s" % (
                        datetime.datetime.now().strftime("%H:%M:%S"), len(games), len(jobs), oname,
                        game["white"], game["black"], result, term, format_stats(summary["stats"]))
                    print(line, flush=True)
                    log.write(line + "\n")
                    log.flush()
                    # Restart engines that forfeited, so one crash doesn't lose the rest of the worker's games.
                    if term.startswith("forfeit"):
                        ea.quit()
                        eb.quit()
                        ea, eb = Engine(a), Engine(b)
        finally:
            ea.quit()
            eb.quit()

    threads = [threading.Thread(target=worker) for _ in range(workers)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    summary = write_summary(final=True)
    line = "FINAL %s (%s vs %s): %s" % (name, a_label, b_label, format_stats(summary["stats"]))
    print(line, flush=True)
    log.write(line + "\n")
    log.close()
    return summary


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--a", required=True, help="candidate engine directory")
    p.add_argument("--b", required=True, help="baseline engine directory")
    p.add_argument("--name", required=True, help="match name (output directory under matches/)")
    p.add_argument("--movetime", type=int, default=1000, help="milliseconds per move (default 1000)")
    p.add_argument("--workers", type=int, default=None, help="games in parallel (default: half the cores)")
    p.add_argument("--games", type=int, default=None, help="play only the first N games (smoke tests)")
    p.add_argument("--out", default=None, help="output root (default: matches/)")
    args = p.parse_args()
    run_match(os.path.abspath(args.a), os.path.abspath(args.b), args.name, args.movetime,
              args.workers, args.games, args.out)


if __name__ == "__main__":
    main()
