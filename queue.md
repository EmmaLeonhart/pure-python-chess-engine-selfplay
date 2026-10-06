# Queue

Concrete next steps. Items are deleted when done (and logged in `devlog.md`).

- Round 0: `matches/round00-v0-vs-v0`, v0 against itself, 200 games at 1 s/move, as a bias check for the runner (expect a score near 50% with an interval containing 0). Record it in README and devlog when it finishes.
- Round 1 candidate (`versions/v1`): killer moves and the history heuristic for quiet-move ordering. Test it, freeze it, and run `round01` against v0 once round 0 is done (one match at a time, so the two don't compete for CPU).
