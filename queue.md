# Queue

Concrete next steps. Items are deleted when done (and logged in `devlog.md`).

- Round 3 (started 09:52 PST, tracked background task): `matches/round03-null-move`, v3 (v2 + null-move pruning) vs v2. Record the result in `match/rounds.json`, re-render the README, and log it. If rejected, `engine/` goes back to v2.
- Round 4 candidate: late move reductions for quiet moves after the first few, with a re-search on fail-high. Build it on the round 3 winner.
- Later: retry killers + history on top of the new best (it scored +40 +- 41 in round 1, just short of the rule).
