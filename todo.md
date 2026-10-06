# Todo (long-term horizon)

- Improvement rounds: at least eight in total, one change each, each a 200-game match at 1 s/move against the current best.
  - A 200-game match resolves only about +-45 Elo. Changes worth roughly 50+ Elo come first, because only those can clear the acceptance rule.
  - Order after round 2 (time management): null-move pruning; late move reductions; principal variation search with aspiration windows; incremental piece-square evaluation for speed; tapered king table and endgame terms; passed pawns and pawn structure; mobility; king safety.
- Results page in README: every round, change, score, Elo +- error, kept or not, final strength.
