# Todo (long-term horizon)

- Round 0: baseline match of v0 against itself to check the runner is unbiased (score should be close to 50%).
- Improvement rounds, at least eight, one change each, each a 200-game match at 1 s/move against the previous best (candidates: killer moves, history heuristic, null-move pruning, late move reductions, PVS, aspiration windows, incremental evaluation for speed, tapered king / endgame tables, passed-pawn and pawn-structure terms, mobility, king safety).
- Results page in README: every round, change, score, Elo +- error, kept or not, final strength.
