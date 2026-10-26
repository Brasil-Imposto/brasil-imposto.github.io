"""Release notes and CHANGELOG.md, one entry per day with production changes (D190, trust spec G3).

A day's notes list every pull request merged into main that day, in Brasília time (UTC-3), one line per task: its title and
its number. The CHANGELOG.md section for the day carries the same lines; the GitHub release of the day uses them as notes.
Usage:
  release-notes.py --date 2026-10-25              print the day's notes
  release-notes.py --changelog                    rebuild CHANGELOG.md from every production day since v1.0.0
  release-notes.py --next-version                 the next tag: v1.N.0, one minor version per production day
The pull requests come from the GitHub REST API through gh (read only); nothing is published by this script.
"""
import argparse
import datetime as dt
import json
import re
import subprocess
from pathlib import Path

REPO = "Brasil-Imposto/brasil-imposto.github.io"
ROOT = Path(__file__).resolve().parents[3]
CHANGELOG = ROOT / "CHANGELOG.md"
BRT = dt.timezone(dt.timedelta(hours=-3))
SINCE = dt.datetime(2026, 10, 22, 14, 6, tzinfo=dt.timezone.utc)  # the v1.0.0 release
HEAD = """# Mudanças publicadas

Uma seção por dia com mudanças na produção (`https://brasil-imposto.github.io`), uma linha por tarefa, com o pull request que a
levou para a `main` (D166, D190). A data é a de Brasília. A versão do dia, quando existe, está nas
[versões do GitHub](https://github.com/Brasil-Imposto/brasil-imposto.github.io/releases).
"""


def production_day(pr):
    """The Brasília date of a pull request merged into main, or None when it is not a production change."""
    if pr.get("base", {}).get("ref") != "main" or not pr.get("merged_at"):
        return None
    merged = dt.datetime.fromisoformat(pr["merged_at"].replace("Z", "+00:00"))
    return merged.astimezone(BRT).date().isoformat() if merged >= SINCE else None


def by_day(prs):
    days = {}
    for pr in prs:
        d = production_day(pr)
        if d:
            days.setdefault(d, []).append(pr)
    for d in days:
        days[d].sort(key=lambda p: p["merged_at"])
    return dict(sorted(days.items(), reverse=True))


def line(pr):
    return f"- {pr['title'].strip()} (#{pr['number']})"


def notes(day, prs):
    return "\n".join(line(p) for p in by_day(prs).get(day, []))


def changelog(prs):
    out = [HEAD]
    for d, items in by_day(prs).items():
        out.append(f"## {d}\n\n" + "\n".join(line(p) for p in items) + "\n")
    return "\n".join(out)


def next_version(tags):
    minors = [int(m.group(1)) for t in tags if (m := re.fullmatch(r"v1\.(\d+)\.0", t))]
    return f"v1.{max(minors, default=0) + 1}.0"


def fetch_prs():
    out = subprocess.run(["gh", "api", f"repos/{REPO}/pulls?state=closed&base=main&per_page=100", "--paginate", "--slurp"],
                         capture_output=True, text=True, check=True).stdout
    return [p for page in json.loads(out) for p in page]


def fetch_tags():
    out = subprocess.run(["gh", "api", f"repos/{REPO}/tags?per_page=100", "--jq", ".[].name"], capture_output=True, text=True, check=True).stdout
    return out.split()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--changelog", action="store_true")
    ap.add_argument("--next-version", action="store_true")
    a = ap.parse_args()
    if a.next_version:
        print(next_version(fetch_tags()))
    elif a.changelog:
        CHANGELOG.write_text(changelog(fetch_prs()), encoding="utf-8")
        print(f"wrote {CHANGELOG.relative_to(ROOT)}")
    elif a.date:
        print(notes(a.date, fetch_prs()))
    else:
        ap.error("one of --date, --changelog, --next-version")
