"""The feature switches (spec BRASIL-IMPOSTO_SPEC_staging_2026-10-23, section 2): data/features.json says, for each feature,
whether the staging build and the production build carry it. A feature switched off is absent from the page (no markup, style or
script of it), never hidden by CSS.

BI_FEATURES_JSON points at another file, for a test build that is never committed. Its schema is schemas/features.schema.json,
checked by pipelines/tests/test_features.py; this module repeats the checks a build needs, with no package beyond Python's own."""
import json
import os
import re
from pathlib import Path

PATH = Path(__file__).resolve().parents[3] / "data" / "features.json"
PROFILES = ("production", "staging")
KEY = re.compile(r"^[a-z][a-z0-9-]*$")


def load():
    return json.loads(Path(os.environ.get("BI_FEATURES_JSON") or PATH).read_text(encoding="utf-8"))


def problems(data):
    out, seen = [], set()
    for i, f in enumerate(data.get("features", [])):
        where = f"features[{i}]"
        if not (isinstance(f.get("key"), str) and KEY.match(f["key"])):
            out.append(f"{where}.key")
        elif f["key"] in seen:
            out.append(f"{where}.key: {f['key']} appears twice")
        else:
            seen.add(f["key"])
        if not (isinstance(f.get("issue"), int) and not isinstance(f.get("issue"), bool) and f["issue"] >= 1):
            out.append(f"{where}.issue")
        for p in PROFILES:
            if not isinstance(f.get(p), bool):
                out.append(f"{where}.{p}: true or false")
    return out


def on(key, profile, data=None):
    """Whether the profile's build carries the feature; an unknown key or profile stops the build."""
    if profile not in PROFILES:
        raise SystemExit(f"features: unknown profile {profile}")
    data = load() if data is None else data
    wrong = problems(data)
    if wrong:
        raise SystemExit("data/features.json: " + "; ".join(wrong))
    for f in data["features"]:
        if f["key"] == key:
            return f[profile]
    raise SystemExit(f"data/features.json: no feature {key}")
