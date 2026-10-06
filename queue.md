# Queue

Concrete next steps. Items are deleted when done (and logged in `devlog.md`).

- Round 1 (started 06:59 PST): `matches/round01-killers-history`, v1 (killers + history) vs v0, 200 games at 1 s/move, with the stall-tolerant runner. Record the result in `match/rounds.json`, re-render the README table, and log it; if rejected, reset `engine/` to v0.
- Round 2 candidate: time management. It is written in `engine/` on top of v1: search until the deadline instead of stopping at half the budget, and keep a timed-out iteration's completed root best. Freeze it as `versions/v2` once round 1 decides the base. If v1 is rejected, re-apply the change to v0's search.py first.
