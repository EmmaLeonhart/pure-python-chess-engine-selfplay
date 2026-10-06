# Queue

Concrete next steps. Items are deleted when done (and logged in `devlog.md`).

- Opening book (`match/openings.txt`): 100 distinct, well-known opening lines of 4-8 plies, as UCI moves from the start position, each checked for legality by a test. Each opening is played once with each colour, so a match is 200 games.
- Match runner (`match/run_match.py`): starts both engines as UCI subprocesses, `go movetime 1000`, games in parallel worker threads (default: half the CPU cores); ends games on mate, stalemate, threefold repetition, 50-move rule and insufficient material, and adjudicates a resignation when both engines report |score| >= 1000 cp for 4 consecutive moves each, or a draw at 300 plies; writes a PGN and a JSON summary to `matches/<name>/`.
- Statistics (`match/stats.py`): score, Elo difference, 95% interval from the per-game score variance; unit tests on known W/D/L cases.
- Write the acceptance rule into README before round 1: keep a change only if the lower end of its 95% Elo interval is above 0.
- Freeze the baseline as `versions/v0/` (a copy of `engine/` and `chess_engine.py`); a smoke match of 4 games at 0.1 s/move to check the runner end to end.
