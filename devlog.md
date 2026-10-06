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
