# Queue

Concrete next steps. Items are deleted when done (and logged in `devlog.md`).

- Round 2 (started 08:32 PST, not a tracked task, so check `matches/round02-full-movetime/log.txt` for the FINAL line): v2 (v0 + full move time) vs v0. Record the result in `match/rounds.json`, re-render the README, and log it. If kept, the best version is v2; if not, `engine/` goes back to v0.
- Round 3 candidate: null-move pruning, written in `engine/` on top of v2: R = 2, not in check, side to move has a piece, not at the root, depth >= 3, static eval >= beta. Depth-5 nodes on three positions: 307k -> 220k. Freeze it as v3 after round 2. If v2 is rejected, re-apply it to v0 first.
- Round 4 candidate: late move reductions for quiet moves after the first few, with a re-search on fail-high.
- Later: retry killers + history on top of the new best (it scored +40 +- 41 in round 1, just short of the rule).
