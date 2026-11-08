"""The monthly split of the support (spec apoie 11.2): who closed weighted issues in a month and their share of what is left after
the infrastructure. Pure: compute(issues, month, pool_cents) takes issues in normalize()'s shape. fetch() reads closed issues from
GitHub through `gh api graphql` (any GitHub login works; the repository is public), so anyone can run it and reach the same cents.

Usage: python3 -m pipelines.support.split_month 2026-12 50000      (the pool in cents, from pipelines.support.ledger.pool_cents)
"""
import json
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

REPO = ("Brasil-Imposto", "brasil-imposto.github.io")
WEIGHTS = {"difficulty:low": 1, "difficulty:medium": 2, "difficulty:high": 3}
TZ = ZoneInfo("America/Sao_Paulo")
QUERY = """query($owner:String!,$name:String!,$cursor:String){repository(owner:$owner,name:$name){issues(first:50,after:$cursor,
states:CLOSED,orderBy:{field:UPDATED_AT,direction:DESC}){pageInfo{hasNextPage endCursor} nodes{number closedAt updatedAt stateReason
labels(first:20){nodes{name}} assignees(first:5){nodes{login}} timelineItems(first:100,itemTypes:[LABELED_EVENT,ASSIGNED_EVENT,
CLOSED_EVENT]){nodes{__typename ... on LabeledEvent{createdAt label{name}} ... on AssignedEvent{createdAt assignee{... on User{login}}}
... on ClosedEvent{createdAt closer{__typename ... on PullRequest{merged}}}}}}}}}"""


def when(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def bounds(month):
    y, m = map(int, month.split("-"))
    return datetime(y, m, 1, tzinfo=TZ), datetime(y + (m == 12), m % 12 + 1, 1, tzinfo=TZ)


def normalize(node):
    items = node["timelineItems"]["nodes"]
    closes = [i for i in items if i["__typename"] == "ClosedEvent"]
    closer = closes[-1]["closer"] if closes else None
    return {"number": node["number"], "closedAt": node["closedAt"], "stateReason": node["stateReason"],
            "closerMerged": bool(closer and closer.get("__typename") == "PullRequest" and closer.get("merged")),
            "labels": [n["name"] for n in node["labels"]["nodes"]],
            "assignees": [n["login"] for n in node["assignees"]["nodes"]],
            "labeled": [{"label": i["label"]["name"], "at": i["createdAt"]} for i in items if i["__typename"] == "LabeledEvent"],
            "assigned": [{"login": (i.get("assignee") or {}).get("login"), "at": i["createdAt"]} for i in items
                         if i["__typename"] == "AssignedEvent"]}


def weight(issue, start, end):
    """The issue's weight and its person, or the reason it does not count."""
    if not (start <= when(issue["closedAt"]) < end):
        return None, "closed outside the month"
    if issue["stateReason"] != "COMPLETED" or not issue["closerMerged"]:
        return None, "not closed by a merged pull request"
    marks = [label for label in issue["labels"] if label in WEIGHTS]
    if len(marks) != 1 or len(issue["assignees"]) != 1:
        return None, "needs one difficulty label and one assignee"
    who = issue["assignees"][0]
    put = [when(x["at"]) for x in issue["labeled"] if x["label"] == marks[0]]
    took = [when(x["at"]) for x in issue["assigned"] if x["login"] == who]
    if not put or not took or max(put) > max(took):
        return None, "the label came after the assignment"
    return WEIGHTS[marks[0]], who


def compute(issues, month, pool_cents):
    start, end = bounds(month)
    per, skipped = {}, []
    for issue in sorted(issues, key=lambda i: i["number"]):
        w, who = weight(issue, start, end)
        if w is None:
            if who != "closed outside the month":
                skipped.append({"number": issue["number"], "reason": who})
            continue
        per.setdefault(who, []).append({"number": issue["number"], "weight": w})
    total = sum(x["weight"] for v in per.values() for x in v)
    shares = [{"login": login, "issues": items, "points": sum(x["weight"] for x in items),
               "amount_cents": pool_cents * sum(x["weight"] for x in items) // total if total else 0}
              for login, items in sorted(per.items(), key=lambda kv: (-sum(x["weight"] for x in kv[1]), kv[0]))]
    return {"month": month, "pool_cents": pool_cents, "shares": shares,
            "kept_cents": pool_cents - sum(s["amount_cents"] for s in shares), "skipped": skipped}


def fetch(month):
    start, _ = bounds(month)
    out, cursor = [], None
    while True:
        args = ["gh", "api", "graphql", "-f", f"query={QUERY}", "-F", f"owner={REPO[0]}", "-F", f"name={REPO[1]}"]
        if cursor:
            args += ["-F", f"cursor={cursor}"]
        page = json.loads(subprocess.run(args, check=True, capture_output=True, text=True).stdout)["data"]["repository"]["issues"]
        out += [normalize(n) for n in page["nodes"]]
        if not page["pageInfo"]["hasNextPage"] or when(page["nodes"][-1]["updatedAt"]) < start:
            return out
        cursor = page["pageInfo"]["endCursor"]


if __name__ == "__main__":
    month, pool = sys.argv[1], int(sys.argv[2])
    print(json.dumps(compute(fetch(month), month, pool), ensure_ascii=False, indent=1))
