# pure-python-chess-engine-selfplay

> Started with [cleanvibe](https://github.com/EmmaLeonhart/cleanvibe) on 2026-10-06.

A chess engine written in pure Python (standard library only), improved one
change at a time by measured self-play. The spec is `data_lake/brief.md`.

## Plan

1. **Engine:** move generation verified against standard perft counts, a UCI
   interface, alpha-beta search with iterative deepening, a transposition
   table and quiescence search.
2. **Match runner:** two engine versions play each other from a fixed set of
   opening positions, both colours, 1 second a move, at least 200 games;
   reports score, Elo difference and its error.
3. **Improvement rounds (8 or more):** one change to search or evaluation per
   round, a full match against the previous best, kept only on a
   statistically clear win.

## Results

_No rounds played yet._ Each round will be listed here: what changed, the
score, the Elo difference with error bars, and whether the change was kept.

## Working on it

Run `cleanvibe` in this folder (or double-click `!runClaude.bat` on Windows) to
open a new Claude session here. It starts with Remote Control on, so you can
continue from the Claude app or web. Earlier sessions are in `sessions/`, and
the running read of the project's purpose is in `INTENT.md`.
