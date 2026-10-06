# Queue

Concrete next steps. Items are deleted when done (and logged in `devlog.md`).

- Board representation (`engine/board.py`): 0x88 or 10x12 mailbox, FEN in/out, make/unmake with castling, en passant, promotion, Zobrist hashing.
- Legal move generation + `tests/test_perft.py`: start position (d4 = 197281) plus Kiwipete and perft positions 3-6 from the Chess Programming Wiki at depth 3-4; mark depth-5+ cases as slow.
- CI: `.github/workflows/ci.yml` running `python -m unittest` on push/PR (fast perft only).
- Search (`engine/search.py`): negamax alpha-beta, iterative deepening, transposition table, quiescence search, time control by deadline; material + piece-square evaluation in `engine/evaluate.py`.
- UCI loop (`engine/uci.py`, entry point `chess_engine.py`): uci, isready, ucinewgame, position, go (movetime/wtime/btime/depth), stop, quit; a test that drives it over pipes.
