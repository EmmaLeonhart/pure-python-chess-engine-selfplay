# Queue

## ⛔ FIRST — STOP ALL CRON JOBS, THEN CONTINUE YOUR CURRENT TASK (Emma, 2026-10-06)

Emma's instruction, relayed by the pc-manager session: **delete every cron job in this session
now (`CronList`, then `CronDelete` each one), and do not create new ones.** Then carry on with
whatever task you are in the middle of, to the end of that task. Too many sessions were running
hourly loops at once and using her tokens all together. Only genealogy, ontology-harness and
shintowiki-scripts keep their crons.

This is not a stop order for your work, and it does not ask you to close the session. When your
current task is done, wait for Emma rather than refilling the queue on your own. Delete this
item once the crons are gone, and note in the devlog that you did it.

Concrete next steps. Items are deleted when done (and logged in `devlog.md`).

- Stop all your cron jobs and continue with your current task.
- BLOCKED-ON-USER-ACTION: round 3 (v3 vs v2). At about 10:02 PST, Claude Code stopped the match because the system was critically low on memory. It had played 24 of 200 games. Its instruction is not to restart it unless the user asks. Emma needs to say to restart it (memory was 9.1 GB free at 10:03). On restart, delete `matches/round03-null-move/` first and run the full 200 games fresh, so the stopped partial run doesn't mix in. Loop ticks must not restart it on their own.
- Round 4 candidate: late move reductions, written in `engine/` on top of v3. Quiet, non-checking moves after the 3rd legal move at depth >= 3 are reduced by 1 (2 after the 8th move at depth >= 6), with a full re-search if they beat alpha. Depth-6 nodes on three positions: 833k -> 228k. Freeze it as v4 after round 3. If v3 is rejected, re-apply it to v2 first.
- Later: retry killers + history on top of the new best (it scored +40 +- 41 in round 1, just short of the rule).
