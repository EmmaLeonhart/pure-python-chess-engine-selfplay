# Queue

Concrete next steps. Items are deleted when done (and logged in `devlog.md`).

- Round 3 (started 09:52 PST, tracked background task): `matches/round03-null-move`, v3 (v2 + null-move pruning) vs v2. Record the result in `match/rounds.json`, re-render the README, and log it. If rejected, `engine/` goes back to v2.
- Round 4 candidate: late move reductions, written in `engine/` on top of v3. Quiet, non-checking moves after the 3rd legal move at depth >= 3 are reduced by 1 (2 after the 8th move at depth >= 6), with a full re-search if they beat alpha. Depth-6 nodes on three positions: 833k -> 228k. Freeze it as v4 after round 3. If v3 is rejected, re-apply it to v2 first.
- Later: retry killers + history on top of the new best (it scored +40 +- 41 in round 1, just short of the rule).
