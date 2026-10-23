"""Photo of each person from Wikidata (P18) and Wikimedia Commons, with author and license.

Keeps only the remote URL; does not download images. Responses are cached in $POLITICIANS_WORK/commons/.
Choosing the entity requires Brazilian citizenship (P27 = Q155) and a public office (P39) or a
description with an office word; the QID stays in the data for human checking.
"""
import json
import hashlib
import re
import subprocess
import time
import urllib.parse

from tse_common import WORK

UA = "BrasilImposto/0.1 (pesquisa civica; contato pelo repositorio do projeto)"
WORDS = re.compile(r"pol[ií]tic|governador|vice|ministr|presidente|deputad|senador|prefeit|economista|advogad|juiz|desembargador|empres", re.I)


def _get(url):
    cache = WORK / "commons" / (hashlib.sha1(url.encode()).hexdigest() + ".json")
    cache.parent.mkdir(parents=True, exist_ok=True)
    if cache.exists():
        return json.loads(cache.read_text())
    for attempt in range(6):
        out = subprocess.run(["curl", "-sS", "-L", "-m", "120", "-A", UA, url], capture_output=True).stdout
        try:
            data = json.loads(out)
            break
        except ValueError:
            time.sleep(3 * (attempt + 1))
    else:
        raise RuntimeError("resposta vazia: " + url)
    cache.write_text(json.dumps(data))
    return data


def _nodash(s):
    """Third-party text (Commons, Wikidata) with no em dash or en dash, by project rule."""
    return s.replace("\u2014", "-").replace("\u2013", "-") if isinstance(s, str) else s


def _strip(html):
    return _nodash(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).strip()) or None


def find_entity(name, hint=None):
    """Returns (qid, entity) of the first Brazilian person with an office who matches the name."""
    q = urllib.parse.urlencode({"action": "wbsearchentities", "search": name, "language": "pt", "uselang": "pt", "type": "item", "limit": 7, "format": "json"})
    hits = _get("https://www.wikidata.org/w/api.php?" + q).get("search", [])
    if not hits:
        return None, None
    ids = "|".join(h["id"] for h in hits)
    ents = _get("https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode({"action": "wbgetentities", "ids": ids, "props": "claims|descriptions", "languages": "pt|en", "format": "json"}))["entities"]
    for h in hits:
        e = ents.get(h["id"], {})
        claims = e.get("claims", {})
        citizen = [c["mainsnak"].get("datavalue", {}).get("value", {}).get("id") for c in claims.get("P27", [])]
        desc = " ".join(d.get("value", "") for d in e.get("descriptions", {}).values())
        if "Q155" not in citizen:
            continue
        if not (claims.get("P39") or WORDS.search(desc)):
            continue
        if hint and not re.search(hint, desc + " " + json.dumps(claims.get("P39", [])), re.I):
            continue
        return h["id"], e
    return None, None


def photo(name, hint=None):
    """{'url','file_page','license','license_url','author','credit','wikidata'} or (None, reason)."""
    qid, ent = find_entity(name, hint)
    if not qid:
        return None, "pessoa nao encontrada no Wikidata com cidadania brasileira e cargo"
    p18 = ent.get("claims", {}).get("P18", [])
    if not p18:
        return None, f"sem imagem (P18) no Wikidata {qid}"
    fname = p18[0]["mainsnak"]["datavalue"]["value"]
    q = urllib.parse.urlencode({"action": "query", "titles": "File:" + fname, "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": 400, "format": "json"})
    pages = _get("https://commons.wikimedia.org/w/api.php?" + q)["query"]["pages"]
    info = next(iter(pages.values())).get("imageinfo", [{}])[0]
    meta = info.get("extmetadata", {})
    val = lambda k: _strip(meta.get(k, {}).get("value"))
    return {
        "url": info.get("thumburl") or info.get("url"),
        "original_url": info.get("url"),
        "file_page": info.get("descriptionurl"),
        "license": val("LicenseShortName"),
        "license_url": val("LicenseUrl"),
        "author": val("Artist"),
        "credit": val("Credit"),
        "wikidata": qid,
        "match_note": "entidade escolhida por nome, cidadania brasileira e cargo; conferir o QID",
    }, None


def _chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def photos_batch(names):
    """Photos for many names with few requests (the Wikidata API limits the rate per request).

    For each name it tries, in this order, the entries 'Nome (politico)', 'Nome (politica)' and 'Nome' of the
    Portuguese Wikipedia; it accepts the first that exists, is not a disambiguation page and whose short description
    (from Wikidata) has an office word. The photo is the entry's main image (pageimages),
    with license and author read on Commons. Returns {name: (photo|None, reason|None)}.
    """
    cands = {n: [f"{n} (político)", f"{n} (política)", n] for n in names}
    titles = sorted({t for ts in cands.values() for t in ts})
    page = {}
    for ch in _chunks(titles, 45):
        q = urllib.parse.urlencode({"action": "query", "titles": "|".join(ch), "redirects": 1, "prop": "pageprops|pageimages",
                                    "piprop": "name", "ppprop": "wikibase_item|disambiguation|wikibase-shortdesc", "format": "json", "formatversion": 2})
        d = _get("https://pt.wikipedia.org/w/api.php?" + q)
        alias = {r["from"]: r["to"] for r in d["query"].get("redirects", []) + d["query"].get("normalized", [])}
        found = {p["title"]: p for p in d["query"]["pages"] if not p.get("missing")}
        for t in ch:
            tt = alias.get(alias.get(t, t), alias.get(t, t))
            if tt in found:
                page[t] = found[tt]
        time.sleep(1)
    qids = sorted({p.get("pageprops", {}).get("wikibase_item") for p in page.values() if p.get("pageprops", {}).get("wikibase_item")})
    wd = {}
    for ch in _chunks(qids, 45):
        q = urllib.parse.urlencode({"action": "wbgetentities", "ids": "|".join(ch), "props": "descriptions|claims", "languages": "pt|en", "format": "json"})
        for qid, e in _get("https://www.wikidata.org/w/api.php?" + q).get("entities", {}).items():
            citizen = [c["mainsnak"].get("datavalue", {}).get("value", {}).get("id") for c in e.get("claims", {}).get("P27", [])]
            desc = _nodash(" ".join(d.get("value", "") for d in e.get("descriptions", {}).values()))
            wd[qid] = (desc, "Q155" in citizen)
        time.sleep(2)
    chosen = {}
    for n, ts in cands.items():
        for t in ts:
            p = page.get(t)
            if not p:
                continue
            pp = p.get("pageprops", {})
            if "disambiguation" in pp:
                continue
            desc, brazilian = wd.get(pp.get("wikibase_item"), ("", False))
            if not brazilian:
                continue
            if not WORDS.search(desc) or re.search(r"futebol|ator|atriz|cantor|músic", desc, re.I):
                continue
            chosen[n] = (p, desc)
            break
    files = sorted({p.get("pageimage") for p, _ in chosen.values() if p.get("pageimage")})
    meta = {}
    for ch in _chunks(files, 45):
        q = urllib.parse.urlencode({"action": "query", "titles": "|".join("File:" + f for f in ch), "prop": "imageinfo",
                                    "iiprop": "url|extmetadata", "iiurlwidth": 400, "format": "json", "formatversion": 2})
        d = _get("https://commons.wikimedia.org/w/api.php?" + q)
        norm_ = {x["to"]: x["from"] for x in d["query"].get("normalized", [])}
        for p in d["query"]["pages"]:
            if p.get("imageinfo"):
                meta[p["title"]] = p["imageinfo"][0]
        time.sleep(1)
    out = {}
    for n in names:
        if n not in chosen:
            out[n] = (None, "verbete da Wikipédia em português com descrição de cargo não encontrado")
            continue
        p, desc = chosen[n]
        img = p.get("pageimage")
        info = meta.get("File:" + (img or "").replace("_", " "))
        if not img or not info:
            out[n] = (None, f"verbete '{p['title']}' sem imagem livre no Wikimedia Commons")
            continue
        m = info.get("extmetadata", {})
        val = lambda k: _strip(m.get(k, {}).get("value"))
        out[n] = ({"url": info.get("thumburl") or info.get("url"), "original_url": info.get("url"), "file_page": info.get("descriptionurl"),
                   "license": val("LicenseShortName"), "license_url": val("LicenseUrl"), "author": val("Artist"), "credit": val("Credit"),
                   "wikidata": p.get("pageprops", {}).get("wikibase_item"), "wikipedia_page": "https://pt.wikipedia.org/wiki/" + p["title"].replace(" ", "_"),
                   "match_note": f"imagem principal do verbete '{p['title']}' ({desc}); conferir que é a pessoa certa"}, None)
    return out
