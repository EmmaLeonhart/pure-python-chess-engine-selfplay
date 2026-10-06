# Queue

Concrete next steps. Items are deleted when done (and logged in `devlog.md`).

- Stop all your cron jobs and continue with your current task.
- BLOCKED-ON-USER-ACTION: round 3 (v3 vs v2). At about 10:02 PST, Claude Code stopped the match because the system was critically low on memory. It had played 24 of 200 games. Its instruction is not to restart it unless the user asks. Emma needs to say to restart it (memory was 9.1 GB free at 10:03). On restart, delete `matches/round03-null-move/` first and run the full 200 games fresh, so the stopped partial run doesn't mix in. Loop ticks must not restart it on their own.
- Round 4 candidate: late move reductions, written in `engine/` on top of v3. Quiet, non-checking moves after the 3rd legal move at depth >= 3 are reduced by 1 (2 after the 8th move at depth >= 6), with a full re-search if they beat alpha. Depth-6 nodes on three positions: 833k -> 228k. Freeze it as v4 after round 3. If v3 is rejected, re-apply it to v2 first.
- Later: retry killers + history on top of the new best (it scored +40 +- 41 in round 1, just short of the rule).
