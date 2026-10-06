# Queue

Concrete next steps. Items are deleted when done (and logged in `devlog.md`).

- Round 0 (started about 04:55 PST): `matches/round00-v0-vs-v0`, v0 against itself, 200 games at 1 s/move, as a bias check for the runner (expect a score near 50% with an interval containing 0). Record it in README and devlog when it finishes.
- Round 1: run `python match/run_match.py --a versions/v1 --b versions/v0 --name round01-killers-history` once round 0 is done (one match at a time). v1 (killers + history) is frozen and committed. Record the result; if rejected, reset `engine/` to v0.
- Round 2 candidate: time management. Use more of the move time: start the next iteration unless more than ~60% of the budget is spent, and keep a timed-out iteration's best move when the previous best has already been searched. Build it from whichever of v0/v1 wins round 1.
