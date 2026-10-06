# Devlog

## 2026-10-06

- 04:38 PST: thirty-minute intake returned WORK MODE (material present, no chat). Wrote `INTENT.md` from `data_lake/brief.md`. Created the GitHub repo `EmmaLeonhart/pure-python-chess-engine-selfplay` as **private**. The brief asks for public, but the launch prompt said private; this is recorded as NEEDS-DECISION in `INTENT.md`.
- cleanvibe update check: the project is on v2.0.4, the latest version, so no skills changed. Recorded the check date in `CLAUDE.md`.
- Filled in `README.md` and planned the work in `queue.md` and `todo.md`.
- 04:51 PST: engine v0 built.
  - `engine/board.py`: 0x88 board, FEN, make/unmake, Zobrist hashing, legal move generation.
  - `engine/evaluate.py`: material and simplified piece-square tables.
  - `engine/search.py`: negamax alpha-beta with iterative deepening, a transposition table, quiescence, check extension and MVV-LVA ordering.
  - `engine/uci.py` and `chess_engine.py`: the UCI interface.
  - Perft passes for all six CPW positions to depth 4, and for the start position and position 3 to depth 5 (`PERFT_SLOW=1`, 68 s).
  - Search and UCI tests pass. Speed is about 80-100k nodes/s; a 1 s search reaches depth 5 from the start position.
  - CI runs `unittest` on push.
- 04:54 PST: match infrastructure built.
  - `match/openings.txt`: 100 distinct, legal opening lines.
  - `match/run_match.py`: a parallel UCI match runner with PGN and JSON output, adjudication, and forfeit on timeouts or illegal moves.
  - `match/stats.py`: score, Elo and 95% interval.
  - The acceptance rule is written in the README.
  - Froze the baseline as `versions/v0`.
  - Smoke match (4 games at 100 ms) ran cleanly. v0 often uses only about half its move time, because it won't start an iteration after half the budget is gone.
- 06:31 PST: round 0 (v0 vs v0, 200 games at 1 s/move) finished.
  - Result: +67 =73 -60, score 51.7%, Elo +12 +- 39 (95% interval -26 to +51). The interval contains 0, so the runner shows no bias. White won 66 games and Black 61.
  - Endings: 104 resignation adjudications, 47 threefold repetitions, 13 checkmates, 11 fifty-move draws, 7 insufficient material, 7 move-limit draws, 1 stalemate.
  - **10 games were forfeits:** "timeout waiting for bestmove", meaning no `bestmove` arrived within movetime + 10 s. They came in two bursts, 05:01-05:04 and 05:32-05:43.
  - Replaying one forfeited game move by move through v0 did not reproduce the hang. Investigating with `--debug` mode (`match/engine_host.py` logs engine stderr and dumps thread stacks on a hang) before round 1. A bug that causes forfeits would distort every later match.
