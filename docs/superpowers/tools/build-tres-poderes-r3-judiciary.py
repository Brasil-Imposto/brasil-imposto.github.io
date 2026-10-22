"""Rebuild only the Judiciary's records of "Os 3 Poderes" from files in git, keeping everything else as the last full build.

build-tres-poderes-r3-data.py builds the whole page's data and needs the raw files of the Câmara, the Senado and the Executive
(data/federal/raw-pay/, outside git). The Judiciary's part needs only data/federal/judiciary-2026.json and
data/federal/positions-2026.json, so it can be rebuilt anywhere; both scripts call the same judiciary_view.record().

Run: python3 docs/superpowers/tools/build-tres-poderes-r3-judiciary.py [--as-before]
--as-before builds the records as they were before D154; on the committed files of that time it must change nothing (the proof).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "pipelines" / "politicians"))
import judiciary_view  # noqa: E402

OUT = ROOT / "data" / "federal" / "officeholders-2026.json"
JS = ROOT / "docs" / "superpowers" / "previews" / "assets" / "tres-poderes-r3-data.js"

out = json.loads(OUT.read_text(encoding="utf-8"))
src = json.loads((ROOT / "data" / "federal" / "judiciary-2026.json").read_text(encoding="utf-8"))
pos = json.loads((ROOT / "data" / "federal" / "positions-2026.json").read_text(encoding="utf-8"))
offices = judiciary_view.offices(pos["positions"])
fresh = {x["id"]: judiciary_view.record(x, offices, apply="--as-before" not in sys.argv) for x in src["people"]}
old = [p["id"] for p in out["people"] if p["house"] == "judiciario"]
assert sorted(old) == sorted(fresh), "the Judiciary's people differ from the last full build: run build-tres-poderes-r3-data.py"
out["people"] = [fresh[p["id"]] if p["house"] == "judiciario" else p for p in out["people"]]
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
JS.write_text("window.TP3 = " + json.dumps(out, ensure_ascii=False) + ";\n", encoding="utf-8")
print(OUT.name, "|", len(fresh), "Judiciary records rebuilt", "(as before D154)" if "--as-before" in sys.argv else "")
