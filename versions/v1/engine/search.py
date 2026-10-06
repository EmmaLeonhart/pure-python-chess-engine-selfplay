"""Search: negamax alpha-beta with iterative deepening, a transposition table and quiescence."""

import time

from engine.board import move_uci
from engine.evaluate import evaluate, VALUE

INF = 1_000_000
MATE = 100_000
MATE_BOUND = MATE - 1000

EXACT, LOWER, UPPER = 0, 1, 2
TT_MAX = 1_000_000


class Timeout(Exception):
    pass


def victim_value(board, m):
    to = (m >> 7) & 127
    v = board.sq[to]
    if v:
        return VALUE[abs(v)]
    if m >> 17 == 2:  # en passant
        return 100
    return 0


class Searcher:
    def __init__(self):
        self.tt = {}
        self.stop = False
        self.nodes = 0
        self.deadline = None
        self.killers = [[0, 0] for _ in range(256)]
        self.history = [0] * (128 * 128)

    def new_game(self):
        self.tt.clear()
        self.history = [0] * (128 * 128)

    # ---- move ordering ----

    def order(self, board, moves, tt_move, ply=-1):
        b = board.sq
        k1, k2 = self.killers[ply] if ply >= 0 else (0, 0)
        hist = self.history
        scored = []
        for m in moves:
            if m == tt_move:
                s = 10_000_000
            else:
                victim = victim_value(board, m)
                promo = (m >> 14) & 7
                if victim or promo:
                    s = 1_000_000 + victim * 10 - VALUE[abs(b[m & 127])] // 100 + (promo and VALUE[promo])
                elif m == k1:
                    s = 900_000
                elif m == k2:
                    s = 800_000
                else:
                    s = min(hist[m & 16383], 700_000)
            scored.append((s, m))
        scored.sort(reverse=True)
        return [m for _, m in scored]

    # ---- search ----

    def check_time(self):
        if self.stop or (self.deadline is not None and time.perf_counter() >= self.deadline):
            raise Timeout

    def qsearch(self, board, alpha, beta, ply):
        self.nodes += 1
        if self.nodes & 1023 == 0:
            self.check_time()
        stand = evaluate(board)
        if stand >= beta:
            return stand
        if stand > alpha:
            alpha = stand
        best = stand
        side = board.side
        for m in self.order(board, board.pseudo_moves(captures_only=True), 0):
            board.make(m)
            if board.attacked(board.king[side], -side):
                board.unmake()
                continue
            score = -self.qsearch(board, -beta, -alpha, ply + 1)
            board.unmake()
            if score > best:
                best = score
                if score > alpha:
                    alpha = score
                    if alpha >= beta:
                        break
        return best

    def negamax(self, board, depth, alpha, beta, ply):
        if ply and (board.halfmove >= 100 or board.is_repetition() or board.insufficient_material()):
            return 0
        side = board.side
        in_check = board.attacked(board.king[side], -side)
        if in_check:
            depth += 1
        if depth <= 0:
            return self.qsearch(board, alpha, beta, ply)
        self.nodes += 1
        if self.nodes & 1023 == 0:
            self.check_time()

        tt_move = 0
        entry = self.tt.get(board.hash)
        if entry is not None:
            e_depth, e_score, e_flag, tt_move = entry
            if ply and e_depth >= depth:
                if e_score > MATE_BOUND:
                    e_score -= ply
                elif e_score < -MATE_BOUND:
                    e_score += ply
                if e_flag == EXACT:
                    return e_score
                if e_flag == LOWER and e_score >= beta:
                    return e_score
                if e_flag == UPPER and e_score <= alpha:
                    return e_score

        alpha_orig = alpha
        best = -INF
        best_move = 0
        legal = 0
        for m in self.order(board, board.pseudo_moves(), tt_move, ply):
            board.make(m)
            if board.attacked(board.king[side], -side):
                board.unmake()
                continue
            legal += 1
            score = -self.negamax(board, depth - 1, -beta, -alpha, ply + 1)
            board.unmake()
            if score > best:
                best = score
                best_move = m
                if ply == 0:
                    self.root_best = m
                if score > alpha:
                    alpha = score
                    if alpha >= beta:
                        if not board.sq[(m >> 7) & 127] and not (m >> 14) & 7 and m >> 17 != 2:
                            killers = self.killers[ply]
                            if killers[0] != m:
                                killers[1] = killers[0]
                                killers[0] = m
                            self.history[m & 16383] += depth * depth
                        break

        if legal == 0:
            return -MATE + ply if in_check else 0

        if best <= alpha_orig:
            flag = UPPER
        elif best >= beta:
            flag = LOWER
        else:
            flag = EXACT
        stored = best
        if stored > MATE_BOUND:
            stored += ply
        elif stored < -MATE_BOUND:
            stored -= ply
        if len(self.tt) >= TT_MAX:
            self.tt.clear()
        self.tt[board.hash] = (depth, stored, flag, best_move)
        return best

    def pv(self, board, max_len=20):
        """Principal variation read back from the transposition table."""
        line = []
        seen = set()
        n = 0
        while n < max_len:
            entry = self.tt.get(board.hash)
            if not entry or not entry[3] or board.hash in seen:
                break
            m = entry[3]
            if m not in board.legal_moves():
                break
            seen.add(board.hash)
            line.append(m)
            board.make(m)
            n += 1
        for _ in range(n):
            board.unmake()
        return line

    def search(self, board, movetime=None, max_depth=64, info=None):
        """Search the position and return the best move (0 if there are no legal moves).

        movetime is in seconds. info, if given, is called with one UCI info line per depth.
        """
        legal = board.legal_moves()
        if not legal:
            return 0
        start = time.perf_counter()
        self.deadline = start + movetime if movetime is not None else None
        self.stop = False
        self.nodes = 0
        best = legal[0]
        self.killers = [[0, 0] for _ in range(256)]
        self.history = [h >> 1 for h in self.history]
        stack_len = len(board.stack)
        for depth in range(1, max_depth + 1):
            self.root_best = 0
            try:
                score = self.negamax(board, depth, -INF, INF, 0)
            except Timeout:
                while len(board.stack) > stack_len:
                    board.unmake()
                break
            if self.root_best:
                best = self.root_best
            elapsed = time.perf_counter() - start
            if info is not None:
                if abs(score) > MATE_BOUND:
                    moves_to_mate = (MATE - abs(score) + 1) // 2
                    score_str = "mate %d" % (moves_to_mate if score > 0 else -moves_to_mate)
                else:
                    score_str = "cp %d" % score
                pv = self.pv(board) or [best]
                info("info depth %d score %s nodes %d time %d nps %d pv %s" % (
                    depth, score_str, self.nodes, int(elapsed * 1000),
                    int(self.nodes / elapsed) if elapsed > 0 else 0, " ".join(move_uci(m) for m in pv)))
            if abs(score) > MATE_BOUND and depth >= MATE - abs(score):
                break
            # The next iteration usually costs several times this one; don't start what can't finish.
            if movetime is not None and elapsed > movetime * 0.5:
                break
        return best
