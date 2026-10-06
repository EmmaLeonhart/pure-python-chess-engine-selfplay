"""Perft counts from the Chess Programming Wiki (https://www.chessprogramming.org/Perft_Results).

Fast cases run by default. Set PERFT_SLOW=1 to run every position to depth 4
(and the start position and position 3 to depth 5), which takes minutes.
"""

import os
import unittest

from engine.board import Board, perft

POSITIONS = {
    "start": ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
              [20, 400, 8902, 197281, 4865609]),
    "kiwipete": ("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
                 [48, 2039, 97862, 4085603]),
    "pos3": ("8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1",
             [14, 191, 2812, 43238, 674624]),
    "pos4": ("r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1",
             [6, 264, 9467, 422333]),
    "pos5": ("rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8",
             [44, 1486, 62379, 2103487]),
    "pos6": ("r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10",
             [46, 2079, 89890, 3894594]),
}

FAST_DEPTH = {"start": 3, "kiwipete": 2, "pos3": 4, "pos4": 3, "pos5": 2, "pos6": 2}
SLOW = os.environ.get("PERFT_SLOW") == "1"


class PerftTest(unittest.TestCase):
    def check(self, name):
        fen, counts = POSITIONS[name]
        max_depth = len(counts) if SLOW else FAST_DEPTH[name]
        if SLOW and name not in ("start", "pos3"):
            max_depth = min(max_depth, 4)
        board = Board(fen)
        for depth in range(1, max_depth + 1):
            with self.subTest(position=name, depth=depth):
                self.assertEqual(perft(board, depth), counts[depth - 1])
        self.assertEqual(board.fen(), fen)  # make/unmake restored the position

    def test_start(self):
        self.check("start")

    def test_kiwipete(self):
        self.check("kiwipete")

    def test_pos3(self):
        self.check("pos3")

    def test_pos4(self):
        self.check("pos4")

    def test_pos5(self):
        self.check("pos5")

    def test_pos6(self):
        self.check("pos6")

    def test_hash_restored(self):
        board = Board(POSITIONS["kiwipete"][0])
        h = board.hash
        for m in board.legal_moves():
            board.make(m)
            self.assertEqual(board.hash, board.compute_hash(), msg=board.fen())
            board.unmake()
        self.assertEqual(board.hash, h)


if __name__ == "__main__":
    unittest.main()
