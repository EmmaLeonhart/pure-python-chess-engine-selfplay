# What this project is for

_Maintained by Claude: a running read of what the user is trying to do. It is
analysis, not a transcript, and it changes as understanding improves._

Work mode started: 2026-10-06 04:38 PST (thirty-minute intake verdict: WORK MODE;
the user said nothing in chat beyond the launch prompt, and `data_lake/brief.md`
was present).

## Current understanding

Build a chess engine in pure Python (standard library only) and improve it by
measured self-play, following `data_lake/brief.md`:

1. Move generation that passes standard perft counts (start position and the
   usual test positions, depth 4+), a UCI interface, alpha-beta search with
   iterative deepening, a transposition table and quiescence search.
2. A match runner: two engine versions, fixed opening set, both colours,
   1 s/move, at least 200 games per match; report score, Elo difference and
   its error.
3. At least eight improvement rounds: one change per round, full match against
   the previous best, keep it only on a statistically clear win, record it.
4. A results page in the README covering every round and the final strength.

The brief calls it a long project: keep going after each round.

## Where it stands

- Engine, perft, UCI and match runner are done.
- Round 0 (bias check) passed.
- Round 1 (killers + history) was rejected at -0.4 to +81.8 Elo. The
  pre-registered rule is applied as written, even for near misses.
- Current best: v0. Round 2 (v2 = full move time) is running.
- Live results are in the README table; history is in `devlog.md`.

## What supports it

- `data_lake/brief.md`: an explicit spec (above).
- Chat: only the launch prompt, which sets the cleanvibe workflow and asks for
  "a private GitHub repo with a descriptive name".
- Folder name: generated, says nothing.

## Constraints from the user

- Launch prompt: work mode creates "a private GitHub repo with a descriptive
  name". The chat takes priority over material in `data_lake/`.
- Standard library only (brief).

## Open questions

- **NEEDS-DECISION (Emma): public or private repo.** The brief says to create
  the repo **public** ("part of public research on how cleanvibe sessions
  work"), overriding CLAUDE.md's private default. The launch prompt in chat
  says private. Chat outranks material, and making it public publishes the
  session transcripts, which can't be undone; making a private repo public
  later is one command. So the repo is created **private**. If Emma confirms
  the brief, run `gh repo edit --visibility public --accept-visibility-change-consequences`.
- Match length (assumption, now measured): games run 8 in parallel on this
  16-core machine. Both sides play under the same conditions, so this is
  taken as fair. Round 0 averaged about 2 games a minute (faster early, slower
  on the later openings), so a 200-game match takes about 1.5-2 hours. Eight
  rounds will take most of a day.
- **The machine is shared.** Other projects run heavy jobs on it, and the
  runner measures scheduling stalls of up to about 5 s. They hit both
  engines at random, so they add noise rather than bias. Games interrupted
  by a stall are replayed (see README). The stalls are reported with each
  match, and the README states this caveat.
- Rounds compare each candidate against the **current best**. Rejected
  changes are dropped, and the next candidate is built on the current best.

## Confidence

High on the goal (explicit brief). The repo visibility is the one open point.
