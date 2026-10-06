import math
import os
import tempfile
import unittest

from engine.board import Board
from match import run_match as run_match_module
from match.run_match import load_openings, run_match, ROOT
from match.stats import match_stats, elo_from_score


class OpeningsTest(unittest.TestCase):
    def test_openings_legal_and_distinct(self):
        openings = load_openings()
        self.assertEqual(len(openings), 100)
        positions = set()
        for name, moves in openings:
            board = Board()
            for s in moves:
                m = board.parse_uci(s)
                self.assertIsNotNone(m, "%s: illegal move %s" % (name, s))
                board.make(m)
            positions.add(board.fen().rsplit(" ", 2)[0])
        self.assertEqual(len(positions), 100)


class StatsTest(unittest.TestCase):
    def test_even_score(self):
        st = match_stats(50, 100, 50)
        self.assertAlmostEqual(st["score"], 0.5)
        self.assertAlmostEqual(st["elo"], 0.0)
        self.assertLess(st["elo_lo"], 0)
        self.assertGreater(st["elo_hi"], 0)

    def test_known_elo(self):
        # A 75% score is about +191 Elo.
        self.assertAlmostEqual(elo_from_score(0.75), 190.85, places=1)

    def test_interval_width(self):
        # 200 games, no draws, 50%: se = 0.5 / sqrt(200) = 0.0354, so the score interval is +-6.9%.
        st = match_stats(100, 0, 100)
        self.assertAlmostEqual(st["score_se"], 0.5 / math.sqrt(200), places=6)
        self.assertAlmostEqual(st["elo_hi"], -st["elo_lo"], places=6)
        self.assertGreater(st["elo_error"], 45)
        self.assertLess(st["elo_error"], 50)

    def test_clear_win(self):
        st = match_stats(80, 80, 40)
        self.assertGreater(st["elo_lo"], 0)


class MatchSmokeTest(unittest.TestCase):
    def test_two_quick_games(self):
        with tempfile.TemporaryDirectory() as out:
            summary = run_match(ROOT, ROOT, "smoke", movetime_ms=30, workers=2, max_games=2, out_root=out)
            self.assertEqual(summary["stats"]["games"], 2)
            for g in summary["games"]:
                self.assertFalse(g["termination"].startswith("forfeit"), g)
            self.assertTrue(os.path.exists(os.path.join(out, "smoke", "games.pgn")))

    def test_stalled_game_is_replayed_then_abandoned(self):
        silent = os.path.join(ROOT, "tests", "fixtures", "silent_engine")
        old = run_match_module.MOVE_GRACE
        run_match_module.MOVE_GRACE = 0.5
        try:
            with tempfile.TemporaryDirectory() as out:
                summary = run_match(silent, silent, "stall", movetime_ms=10, workers=1, max_games=1,
                                    out_root=out)
        finally:
            run_match_module.MOVE_GRACE = old
        self.assertIsNone(summary["stats"])  # no game counted
        self.assertEqual(len(summary["replays"]), run_match_module.MAX_ATTEMPTS - 1)
        self.assertEqual(len(summary["abandoned"]), 1)


if __name__ == "__main__":
    unittest.main()
