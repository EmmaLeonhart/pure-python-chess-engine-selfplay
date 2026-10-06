"""Render the README results table from match/rounds.json and matches/*/summary.json.

Run after recording a round in match/rounds.json: python match/results.py
It rewrites the part of README.md between the RESULTS markers.
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

START = "<!-- RESULTS START -->"
END = "<!-- RESULTS END -->"


def load_rounds():
    with open(os.path.join(ROOT, "match", "rounds.json")) as f:
        return json.load(f)


def table(rounds):
    rows = ["| Round | Candidate vs baseline | Change | W / D / L | Score | Elo (95% interval) | Kept |",
            "|---|---|---|---|---|---|---|"]
    for r in rounds:
        path = os.path.join(ROOT, "matches", r["match"], "summary.json")
        if not os.path.exists(path):
            continue
        with open(path) as f:
            summary = json.load(f)
        st = summary["stats"]
        kept = r["kept"]
        if not summary.get("finished"):
            kept = "running (%d/%d games)" % (st["games"], summary["planned_games"])
        rows.append("| %s | %s vs %s | %s | %d / %d / %d | %.1f%% | %+.0f +- %.0f (%+.1f to %+.1f) | %s |" % (
            r["round"], r["candidate"], r["baseline"], r["change"], st["wins"], st["draws"], st["losses"],
            100 * st["score"], st["elo"], st["elo_error"], st["elo_lo"], st["elo_hi"], kept))
    return "\n".join(rows)


def main():
    rounds = load_rounds()
    readme_path = os.path.join(ROOT, "README.md")
    with open(readme_path) as f:
        text = f.read()
    if START not in text or END not in text:
        sys.exit("README.md has no results markers")
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    with open(readme_path, "w") as f:
        f.write(head + START + "\n" + table(rounds) + "\n" + END + tail)
    print(table(rounds))


if __name__ == "__main__":
    main()
