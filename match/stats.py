"""Match statistics: score, Elo difference and a 95% interval from per-game score variance."""

import math

Z95 = 1.959964


def elo_from_score(s):
    if s <= 0:
        return -math.inf
    if s >= 1:
        return math.inf
    return -400.0 * math.log10(1.0 / s - 1.0)


def match_stats(wins, draws, losses):
    """Stats for the first engine, given its wins, draws and losses.

    The interval treats each game as an independent draw from a {1, 0.5, 0}
    outcome distribution: the score's standard error is the per-game standard
    deviation over sqrt(n), and the Elo bounds are the score bounds converted
    to Elo.
    """
    n = wins + draws + losses
    if n == 0:
        raise ValueError("no games")
    s = (wins + 0.5 * draws) / n
    var = (wins * (1 - s) ** 2 + draws * (0.5 - s) ** 2 + losses * s ** 2) / n
    se = math.sqrt(var / n)
    lo, hi = s - Z95 * se, s + Z95 * se
    elo = elo_from_score(s)
    elo_lo = elo_from_score(lo)
    elo_hi = elo_from_score(hi)
    return {
        "games": n, "wins": wins, "draws": draws, "losses": losses,
        "score": s, "score_se": se,
        "elo": elo, "elo_lo": elo_lo, "elo_hi": elo_hi,
        # Half-width of the interval, for "+- error" reporting.
        "elo_error": (elo_hi - elo_lo) / 2,
    }


def format_stats(st):
    return "%d games: +%d =%d -%d, score %.1f%%, Elo %+.1f +- %.1f (95%% interval %+.1f to %+.1f)" % (
        st["games"], st["wins"], st["draws"], st["losses"], 100 * st["score"],
        st["elo"], st["elo_error"], st["elo_lo"], st["elo_hi"])
