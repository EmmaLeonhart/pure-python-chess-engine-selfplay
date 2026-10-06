import os
import subprocess
import sys
import unittest

from engine.board import Board, move_uci
from engine.search import Searcher

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class SearchTest(unittest.TestCase):
    def best(self, fen, depth):
        board = Board(fen)
        move = Searcher().search(board, max_depth=depth)
        self.assertEqual(board.fen(), fen)  # search left the board as it found it
        return move_uci(move)

    def test_mate_in_one(self):
        self.assertEqual(self.best("6k1/5ppp/8/8/8/8/5PPP/R5K1 w - - 0 1", 2), "a1a8")

    def test_mate_in_two(self):
        # 1. Qe8+ Rxe8 2. Rxe8# (or 1. Re8+ Rxe8 2. Qxe8#)
        self.assertIn(self.best("1r4k1/5ppp/8/8/8/8/4QPPP/4R1K1 w - - 0 1", 4), ("e2e8", "e1e8"))

    def test_wins_hanging_queen(self):
        self.assertEqual(self.best("4k3/8/8/3q4/8/8/8/3RK3 w - - 0 1", 3), "d1d5")

    def test_no_legal_moves(self):
        board = Board("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")  # stalemate
        self.assertEqual(Searcher().search(board, max_depth=3), 0)

    def test_time_limit(self):
        board = Board()
        fen = board.fen()
        move = Searcher().search(board, movetime=0.3)
        self.assertIn(move, board.legal_moves())
        self.assertEqual(board.fen(), fen)


class UCITest(unittest.TestCase):
    def test_uci_session(self):
        commands = "\n".join([
            "uci", "isready", "ucinewgame",
            "position startpos moves e2e4 e7e5",
            "go movetime 300", "isready", "quit"]) + "\n"
        proc = subprocess.run([sys.executable, os.path.join(ROOT, "chess_engine.py")], input=commands,
                              capture_output=True, text=True, timeout=60)
        lines = proc.stdout.splitlines()
        self.assertIn("uciok", lines)
        best = [l for l in lines if l.startswith("bestmove")]
        self.assertEqual(len(best), 1, proc.stdout)
        board = Board()
        for s in ("e2e4", "e7e5"):
            board.make(board.parse_uci(s))
        self.assertIsNotNone(board.parse_uci(best[0].split()[1]))


if __name__ == "__main__":
    unittest.main()
