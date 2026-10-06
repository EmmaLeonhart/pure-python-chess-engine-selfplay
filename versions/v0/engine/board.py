"""Board representation: 0x88 mailbox, FEN, make/unmake, Zobrist hashing, legal moves.

Squares are 0x88 indices (rank * 16 + file, rank 0 = rank 1). Pieces are ints:
pawn 1, knight 2, bishop 3, rook 4, queen 5, king 6; positive for white,
negative for black. The side to move is 1 (white) or -1 (black).

A move is an int: from | to << 7 | promo << 14 | flag << 17, where promo is a
piece type (0 if none) and flag is one of QUIET, DOUBLE, EP, CASTLE.
"""

import random

PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING = 1, 2, 3, 4, 5, 6
WHITE, BLACK = 1, -1

QUIET, DOUBLE, EP, CASTLE = 0, 1, 2, 3

KNIGHT_DIRS = (33, 31, 18, 14, -33, -31, -18, -14)
BISHOP_DIRS = (17, 15, -17, -15)
ROOK_DIRS = (16, 1, -16, -1)
KING_DIRS = BISHOP_DIRS + ROOK_DIRS

SQUARES = tuple(r * 16 + f for r in range(8) for f in range(8))

PIECE_CHARS = {PAWN: "p", KNIGHT: "n", BISHOP: "b", ROOK: "r", QUEEN: "q", KING: "k"}
CHAR_PIECES = {c: p for p, c in PIECE_CHARS.items()}

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

# Castling rights: 1 = white king side, 2 = white queen side, 4 = black king side, 8 = black queen side.
CASTLE_MASK = [15] * 128
CASTLE_MASK[0x00] = 15 & ~2   # a1
CASTLE_MASK[0x07] = 15 & ~1   # h1
CASTLE_MASK[0x04] = 15 & ~3   # e1
CASTLE_MASK[0x70] = 15 & ~8   # a8
CASTLE_MASK[0x77] = 15 & ~4   # h8
CASTLE_MASK[0x74] = 15 & ~12  # e8

_rng = random.Random(20261006)
Z_PIECE = [[_rng.getrandbits(64) for _ in range(128)] for _ in range(13)]  # index piece + 6
Z_CASTLE = [_rng.getrandbits(64) for _ in range(16)]
Z_EP = [_rng.getrandbits(64) for _ in range(8)]
Z_SIDE = _rng.getrandbits(64)


def move_from(m):
    return m & 127


def move_to(m):
    return (m >> 7) & 127


def move_promo(m):
    return (m >> 14) & 7


def move_flag(m):
    return m >> 17


def make_move(frm, to, promo=0, flag=QUIET):
    return frm | (to << 7) | (promo << 14) | (flag << 17)


def sq_name(sq):
    return "abcdefgh"[sq & 7] + str((sq >> 4) + 1)


def parse_sq(name):
    return (int(name[1]) - 1) * 16 + "abcdefgh".index(name[0])


def move_uci(m):
    s = sq_name(move_from(m)) + sq_name(move_to(m))
    promo = move_promo(m)
    if promo:
        s += PIECE_CHARS[promo]
    return s


class Board:
    def __init__(self, fen=START_FEN):
        self.set_fen(fen)

    # ---- setup ----

    def set_fen(self, fen):
        parts = fen.split()
        self.sq = [0] * 128
        self.king = {WHITE: -1, BLACK: -1}
        rank = 7
        file = 0
        for c in parts[0]:
            if c == "/":
                rank -= 1
                file = 0
            elif c.isdigit():
                file += int(c)
            else:
                p = CHAR_PIECES[c.lower()] * (WHITE if c.isupper() else BLACK)
                s = rank * 16 + file
                self.sq[s] = p
                if abs(p) == KING:
                    self.king[WHITE if p > 0 else BLACK] = s
                file += 1
        self.side = WHITE if parts[1] == "w" else BLACK
        self.castling = 0
        cr = parts[2] if len(parts) > 2 else "-"
        for c, bit in (("K", 1), ("Q", 2), ("k", 4), ("q", 8)):
            if c in cr:
                self.castling |= bit
        self.ep = parse_sq(parts[3]) if len(parts) > 3 and parts[3] != "-" else -1
        self.halfmove = int(parts[4]) if len(parts) > 4 else 0
        self.fullmove = int(parts[5]) if len(parts) > 5 else 1
        self.stack = []
        self.hash = self.compute_hash()
        self.history = [self.hash]

    def compute_hash(self):
        h = 0
        for s in SQUARES:
            p = self.sq[s]
            if p:
                h ^= Z_PIECE[p + 6][s]
        h ^= Z_CASTLE[self.castling]
        if self.ep != -1:
            h ^= Z_EP[self.ep & 7]
        if self.side == BLACK:
            h ^= Z_SIDE
        return h

    def fen(self):
        rows = []
        for rank in range(7, -1, -1):
            row = ""
            empty = 0
            for file in range(8):
                p = self.sq[rank * 16 + file]
                if p == 0:
                    empty += 1
                    continue
                if empty:
                    row += str(empty)
                    empty = 0
                c = PIECE_CHARS[abs(p)]
                row += c.upper() if p > 0 else c
            if empty:
                row += str(empty)
            rows.append(row)
        cr = "".join(c for c, bit in (("K", 1), ("Q", 2), ("k", 4), ("q", 8)) if self.castling & bit) or "-"
        ep = sq_name(self.ep) if self.ep != -1 else "-"
        return "%s %s %s %s %d %d" % ("/".join(rows), "w" if self.side == WHITE else "b", cr, ep,
                                      self.halfmove, self.fullmove)

    # ---- attacks ----

    def attacked(self, s, by):
        """True if square s is attacked by side `by`."""
        b = self.sq
        # pawns: a white pawn on s-15 or s-17 attacks s
        if by == WHITE:
            t = s - 15
            if not t & 0x88 and b[t] == PAWN:
                return True
            t = s - 17
            if not t & 0x88 and b[t] == PAWN:
                return True
        else:
            t = s + 15
            if not t & 0x88 and b[t] == -PAWN:
                return True
            t = s + 17
            if not t & 0x88 and b[t] == -PAWN:
                return True
        knight = KNIGHT * by
        for d in KNIGHT_DIRS:
            t = s + d
            if not t & 0x88 and b[t] == knight:
                return True
        king = KING * by
        for d in KING_DIRS:
            t = s + d
            if not t & 0x88 and b[t] == king:
                return True
        bishop, rook, queen = BISHOP * by, ROOK * by, QUEEN * by
        for d in BISHOP_DIRS:
            t = s + d
            while not t & 0x88:
                p = b[t]
                if p:
                    if p == bishop or p == queen:
                        return True
                    break
                t += d
        for d in ROOK_DIRS:
            t = s + d
            while not t & 0x88:
                p = b[t]
                if p:
                    if p == rook or p == queen:
                        return True
                    break
                t += d
        return False

    def in_check(self, side=None):
        if side is None:
            side = self.side
        return self.attacked(self.king[side], -side)

    # ---- move generation ----

    def pseudo_moves(self, captures_only=False):
        b = self.sq
        side = self.side
        moves = []
        add = moves.append
        fwd = 16 * side
        start_rank = 1 if side == WHITE else 6
        promo_rank = 7 if side == WHITE else 0
        for frm in SQUARES:
            p = b[frm]
            if p == 0 or (p > 0) != (side > 0):
                continue
            kind = p if p > 0 else -p
            if kind == PAWN:
                to = frm + fwd
                for cto in (to - 1, to + 1):
                    if cto & 0x88:
                        continue
                    t = b[cto]
                    if t and (t > 0) != (side > 0):
                        if cto >> 4 == promo_rank:
                            for pr in (QUEEN, ROOK, BISHOP, KNIGHT):
                                add(frm | cto << 7 | pr << 14)
                        else:
                            add(frm | cto << 7)
                    elif cto == self.ep:
                        add(frm | cto << 7 | EP << 17)
                if not b[to]:
                    if to >> 4 == promo_rank:
                        add(frm | to << 7 | QUEEN << 14)
                        if not captures_only:
                            for pr in (ROOK, BISHOP, KNIGHT):
                                add(frm | to << 7 | pr << 14)
                    elif not captures_only:
                        add(frm | to << 7)
                        if frm >> 4 == start_rank and not b[to + fwd]:
                            add(frm | (to + fwd) << 7 | DOUBLE << 17)
            elif kind == KNIGHT or kind == KING:
                for d in (KNIGHT_DIRS if kind == KNIGHT else KING_DIRS):
                    to = frm + d
                    if to & 0x88:
                        continue
                    t = b[to]
                    if t == 0:
                        if not captures_only:
                            add(frm | to << 7)
                    elif (t > 0) != (side > 0):
                        add(frm | to << 7)
                if kind == KING and not captures_only:
                    self._castles(frm, add)
            else:
                dirs = BISHOP_DIRS if kind == BISHOP else ROOK_DIRS if kind == ROOK else KING_DIRS
                for d in dirs:
                    to = frm + d
                    while not to & 0x88:
                        t = b[to]
                        if t == 0:
                            if not captures_only:
                                add(frm | to << 7)
                        else:
                            if (t > 0) != (side > 0):
                                add(frm | to << 7)
                            break
                        to += d
        return moves

    def _castles(self, frm, add):
        b = self.sq
        side = self.side
        if side == WHITE:
            if frm != 0x04:
                return
            ks, qs = 1, 2
        else:
            if frm != 0x74:
                return
            ks, qs = 4, 8
        cr = self.castling
        if not cr & (ks | qs):
            return
        if self.attacked(frm, -side):
            return
        if cr & ks and not b[frm + 1] and not b[frm + 2] and b[frm + 3] == ROOK * side:
            if not self.attacked(frm + 1, -side) and not self.attacked(frm + 2, -side):
                add(frm | (frm + 2) << 7 | CASTLE << 17)
        if cr & qs and not b[frm - 1] and not b[frm - 2] and not b[frm - 3] and b[frm - 4] == ROOK * side:
            if not self.attacked(frm - 1, -side) and not self.attacked(frm - 2, -side):
                add(frm | (frm - 2) << 7 | CASTLE << 17)

    def legal_moves(self, captures_only=False):
        side = self.side
        out = []
        for m in self.pseudo_moves(captures_only):
            self.make(m)
            if not self.attacked(self.king[side], -side):
                out.append(m)
            self.unmake()
        return out

    # ---- make / unmake ----

    def make(self, m):
        frm = m & 127
        to = (m >> 7) & 127
        promo = (m >> 14) & 7
        flag = m >> 17
        b = self.sq
        side = self.side
        p = b[frm]
        cap = b[to]
        self.stack.append((m, cap, self.castling, self.ep, self.halfmove, self.hash))
        h = self.hash
        if self.ep != -1:
            h ^= Z_EP[self.ep & 7]
        h ^= Z_CASTLE[self.castling]
        h ^= Z_PIECE[p + 6][frm]
        b[frm] = 0
        if cap:
            h ^= Z_PIECE[cap + 6][to]
        if flag == EP:
            capsq = to - 16 * side
            h ^= Z_PIECE[-side * PAWN + 6][capsq]
            b[capsq] = 0
        newp = promo * side if promo else p
        b[to] = newp
        h ^= Z_PIECE[newp + 6][to]
        if flag == CASTLE:
            if to > frm:
                rf, rt = frm + 3, frm + 1
            else:
                rf, rt = frm - 4, frm - 1
            r = b[rf]
            b[rf] = 0
            b[rt] = r
            h ^= Z_PIECE[r + 6][rf] ^ Z_PIECE[r + 6][rt]
        if p == KING * side:
            self.king[side] = to
        self.castling &= CASTLE_MASK[frm] & CASTLE_MASK[to]
        h ^= Z_CASTLE[self.castling]
        if flag == DOUBLE:
            self.ep = (frm + to) >> 1
            h ^= Z_EP[self.ep & 7]
        else:
            self.ep = -1
        if cap or p == PAWN * side:
            self.halfmove = 0
        else:
            self.halfmove += 1
        if side == BLACK:
            self.fullmove += 1
        self.side = -side
        h ^= Z_SIDE
        self.hash = h
        self.history.append(h)

    def unmake(self):
        m, cap, castling, ep, halfmove, h = self.stack.pop()
        self.history.pop()
        frm = m & 127
        to = (m >> 7) & 127
        promo = (m >> 14) & 7
        flag = m >> 17
        side = -self.side
        self.side = side
        b = self.sq
        p = PAWN * side if promo else b[to]
        b[frm] = p
        b[to] = cap
        if flag == EP:
            b[to - 16 * side] = -side * PAWN
        elif flag == CASTLE:
            if to > frm:
                rf, rt = frm + 3, frm + 1
            else:
                rf, rt = frm - 4, frm - 1
            b[rf] = b[rt]
            b[rt] = 0
        if p == KING * side:
            self.king[side] = frm
        self.castling = castling
        self.ep = ep
        self.halfmove = halfmove
        self.hash = h
        if side == BLACK:
            self.fullmove -= 1

    def make_null(self):
        self.stack.append((0, 0, self.castling, self.ep, self.halfmove, self.hash))
        h = self.hash
        if self.ep != -1:
            h ^= Z_EP[self.ep & 7]
        self.ep = -1
        self.halfmove += 1
        self.side = -self.side
        h ^= Z_SIDE
        self.hash = h
        self.history.append(h)

    def unmake_null(self):
        _, _, castling, ep, halfmove, h = self.stack.pop()
        self.history.pop()
        self.side = -self.side
        self.castling = castling
        self.ep = ep
        self.halfmove = halfmove
        self.hash = h

    # ---- helpers ----

    def parse_uci(self, s):
        """Return the legal move matching UCI string s, or None."""
        for m in self.legal_moves():
            if move_uci(m) == s:
                return m
        return None

    def is_repetition(self, count=1):
        """True if the current position occurred `count` times before, within the halfmove window."""
        h = self.hash
        hist = self.history
        n = 0
        i = len(hist) - 3
        stop = max(0, len(hist) - 1 - self.halfmove)
        while i >= stop:
            if hist[i] == h:
                n += 1
                if n >= count:
                    return True
            i -= 2
        return False

    def insufficient_material(self):
        minors = 0
        for s in SQUARES:
            p = self.sq[s]
            if p == 0:
                continue
            k = abs(p)
            if k == PAWN or k == ROOK or k == QUEEN:
                return False
            if k == KNIGHT or k == BISHOP:
                minors += 1
        return minors <= 1


def perft(board, depth):
    if depth == 0:
        return 1
    moves = board.legal_moves()
    if depth == 1:
        return len(moves)
    n = 0
    for m in moves:
        board.make(m)
        n += perft(board, depth - 1)
        board.unmake()
    return n
