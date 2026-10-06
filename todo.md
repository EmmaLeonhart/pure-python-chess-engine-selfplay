# Todo (long-term horizon)

- Match runner: two engine versions (frozen copies under `versions/`) play over UCI from a fixed opening set, both colours, 1 s/move, >= 200 games, games run in parallel processes; adjudicate mate, stalemate, repetition, 50-move rule, insufficient material; report W/D/L, score, Elo difference and 95% error; save PGN and a JSON summary under `matches/`.
- Statistical acceptance rule for a round (e.g. Elo lower bound of the 95% interval > 0, or SPRT), written down before round 1.
- Improvement rounds, at least eight, one change each (candidates: move ordering with MVV-LVA and killers, history heuristic, null-move pruning, late move reductions, PVS, aspiration windows, check extensions, king safety / mobility / pawn-structure evaluation, tapered eval).
- Results page in README: every round, change, score, Elo +- error, kept or not, final strength.
