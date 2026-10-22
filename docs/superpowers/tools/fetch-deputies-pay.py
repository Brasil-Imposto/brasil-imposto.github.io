"""Collects, for every federal deputy in office, what the Câmara publishes on the deputy's own page for one year: gross salary,
official flat, housing allowance, diplomatic passport, missions abroad, and the quota (Ceap) and office budget used, month by
month. One request per deputy, about one per second; resumable: deputies already in the output are skipped.

Usage: uv run python docs/superpowers/tools/fetch-deputies-pay.py [YEAR]
Writes data/federal/raw-pay/deputies-pay-YEAR.jsonl (one parsed deputy per line, with the page's SHA-256; the HTML is not kept)
and data/federal/raw-pay/deputies-in-office.json (the Câmara's list of deputies in office, from its open data API).
"""
import hashlib, html, json, re, subprocess, sys, time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
YEAR = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
RAW = ROOT / "data" / "federal" / "raw-pay"
OUT = RAW / f"deputies-pay-{YEAR}.jsonl"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
MON = {"JAN": 1, "FEV": 2, "MAR": 3, "ABR": 4, "MAI": 5, "JUN": 6, "JUL": 7, "AGO": 8, "SET": 9, "OUT": 10, "NOV": 11, "DEZ": 12}
brl = lambda s: float(s.replace(".", "").replace(",", "."))


def get(url, accept="text/html"):
    for attempt in range(4):
        r = subprocess.run(["curl", "-sS", "-L", "--compressed", "-m", "60", "-A", UA, "-H", f"Accept: {accept}", url], capture_output=True)
        if r.returncode == 0 and len(r.stdout) > 2000:
            return r.stdout
        time.sleep(5 * (attempt + 1))
    raise SystemExit(f"could not fetch {url}")


def text_of(raw):
    t = raw.decode("utf-8", "ignore")
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", t, flags=re.S | re.I)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))


def block(t, label, nxt):
    i = t.find(label + " ? Percentual gasto")
    if i < 0:
        return None
    seg = t[i:]; seg = seg[:seg.index(nxt)] if nxt in seg else seg[:2500]
    m = re.search(r"Total \(R\$\) Percentual Gasto ([\d.]+,\d{2}) ([\d.]+)%", seg)
    if not m and "Ainda não há gasto registrado neste ano" in seg:
        return {"used_year": 0.0, "used_pct": 0.0, "by_month": {}, "none_registered": True}
    if not m:
        return None
    months = {MON[k]: brl(v) for k, v in re.findall(r"\b(JAN|FEV|MAR|ABR|MAI|JUN|JUL|AGO|SET|OUT|NOV|DEZ) ([\d.]+,\d{2})", seg)}
    return {"used_year": brl(m.group(1)), "used_pct": float(m.group(2)), "by_month": months}


def parse(dep_id, raw):
    t = text_of(raw)
    field = lambda pat: (re.search(pat, t) or [None, None])[1]
    sal = field(r"Salário mensal bruto \? R\$ ([\d.]+,\d{2})")
    return {"id": dep_id, "sha256": hashlib.sha256(raw).hexdigest(),
            "updated": field(r"Informações de recursos atualizadas em (\d{2}/\d{2}/\d{4} \d{2}:\d{2})"),
            "salary_gross": brl(sal) if sal else None,
            "flat": (field(r"Imóvel funcional \? (.+?) Auxílio-moradia") or "").strip() or None,
            "housing": (field(r"Auxílio-moradia \? (.+?) Viagens em missão oficial") or "").strip() or None,
            "missions": field(r"Viagens em missão oficial \? (\d+)"),
            "passport": field(r"Passaporte diplomático \? (\S+)"),
            "ceap": block(t, "Cota parlamentar", "Verba de gabinete ?"),
            "office": block(t, "Verba de gabinete", "Salário mensal bruto")}


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    lst = json.loads(get("https://dadosabertos.camara.leg.br/api/v2/deputados?ordem=ASC&ordenarPor=nome&itens=1000", "application/json"))
    deps = lst["dados"]
    (RAW / "deputies-in-office.json").write_text(json.dumps({"fetched_on": date.today().isoformat(), "count": len(deps), "dados": deps}, ensure_ascii=False))
    done = {json.loads(l)["id"] for l in OUT.read_text().splitlines()} if OUT.exists() else set()
    print(len(deps), "deputies in office;", len(done), "already collected", flush=True)
    with OUT.open("a", encoding="utf-8") as f:
        for i, d in enumerate(deps, 1):
            if d["id"] in done:
                continue
            raw = get(f"https://www.camara.leg.br/deputados/{d['id']}?ano={YEAR}")
            rec = parse(d["id"], raw)
            rec.update({"name": d["nome"], "party": d["siglaPartido"], "uf": d["siglaUf"], "photo": d["urlFoto"]})
            f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            if i % 25 == 0:
                print(i, "of", len(deps), flush=True)
            time.sleep(1.1)
    print("done", sum(1 for _ in OUT.open()), "lines", flush=True)


if __name__ == "__main__":
    main()
