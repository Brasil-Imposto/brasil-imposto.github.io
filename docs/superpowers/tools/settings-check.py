"""The repository settings the donation's security asks for (spec seguranca-doacoes, section 5), read through the API with this
machine's gh: an active ruleset on each branch that publishes (pull requests only, no force push, no deletion, the required checks),
and Actions limited to selected actions pinned by a full commit SHA. Prints every difference; exit 1 if any. Rulesets on every
repository that deploys: Homebrew's organization rulesets cover its websites; actions pinned by SHA by policy: Kubernetes, Semgrep.

Run: python3 docs/superpowers/tools/settings-check.py [--control]   (--control adds a rule nobody has: it must be reported)
"""
import json
import subprocess
import sys

BASE = {"deletion", "non_fast_forward", "pull_request", "required_status_checks"}
EXPECTED = {
    "Brasil-Imposto/brasil-imposto.github.io": {
        "branches": {"main": {"rules": BASE, "checks": {"dco", "ci", "security", "guard"}},
                     "staging": {"rules": BASE | {"code_scanning"}, "checks": {"dco", "ci", "visible-text", "security", "guard"}}},
        "actions": {"allowed_actions": "selected", "sha_pinning_required": True}},
    "Brasil-Imposto/staging": {
        "branches": {"main": {"rules": BASE, "checks": {"dco"}}},
        "actions": {"allowed_actions": "selected", "sha_pinning_required": True}},
}


def gh(path):
    return json.loads(subprocess.run(["gh", "api", path], check=True, capture_output=True, text=True).stdout)


def actual(repo):
    """Per branch, the rule types and required checks of every active ruleset that names it; and the Actions policy."""
    branches = {}
    for r in gh(f"repos/{repo}/rulesets"):
        full = gh(f"repos/{repo}/rulesets/{r['id']}")
        if full.get("enforcement") != "active" or full.get("target") != "branch":
            continue
        for ref in full.get("conditions", {}).get("ref_name", {}).get("include", []):
            b = branches.setdefault(ref.removeprefix("refs/heads/"), {"rules": set(), "checks": set()})
            for rule in full.get("rules", []):
                b["rules"].add(rule["type"])
                if rule["type"] == "required_status_checks":
                    b["checks"] |= {c["context"] for c in rule["parameters"]["required_status_checks"]}
    perms = gh(f"repos/{repo}/actions/permissions")
    return {"branches": branches, "actions": {k: perms.get(k) for k in ("allowed_actions", "sha_pinning_required")}}


def problems(repo, got, want):
    out = []
    for branch, w in want["branches"].items():
        g = got["branches"].get(branch, {"rules": set(), "checks": set()})
        out += [f"{repo} {branch}: no {r} rule" for r in sorted(w["rules"] - g["rules"])]
        out += [f"{repo} {branch}: check {c} not required" for c in sorted(w["checks"] - g["checks"])]
    out += [f"{repo} actions: {k} is {got['actions'].get(k)!r}, not {v!r}" for k, v in want["actions"].items() if got["actions"].get(k) != v]
    return out


if __name__ == "__main__":
    want = json.loads(json.dumps(EXPECTED, default=sorted))
    for repo in want:
        for b in want[repo]["branches"].values():
            b["rules"], b["checks"] = set(b["rules"]), set(b["checks"])
        if "--control" in sys.argv:
            next(iter(want[repo]["branches"].values()))["rules"].add("required_signatures")
    found = [p for repo, w in want.items() for p in problems(repo, actual(repo), w)]
    print("\n".join(found) or "every setting as expected")
    sys.exit(1 if found else 0)
