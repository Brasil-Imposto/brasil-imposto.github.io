"""The ci's visible-text check (spec paridade-enderecos-formatador, part A; D194): on a pull request, the published site is built
from the pull request and from its base, and the visible text of the four pages is compared: Início in the 100 combinations of
visible-text-probe.cjs (19 periods, and the 27 state panels in a year, a mandate and a month) and the whole text of Os 3 Poderes,
Como o dinheiro anda and Como ler o mapa. Pages are matched by their key (site_chrome.ALL_PAGES), so a renamed page still compares.
Any difference fails, unless the pull request carries the label muda-a-tela. A pull request that touches nothing that builds the
pages passes at once.
Usage: visible-text-check.py --base <checkout of the base> --pr <checkout of the pull request> [--label]
Env: PW_CORE and CHROME_HEADLESS as for visible-text-probe.cjs (CHROME_HEADLESS may be left out where playwright installed it).
"""
import argparse
import functools
import http.server
import importlib.util
import json
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

# what builds the pages; a pull request that touches none of it cannot change their text
BUILDS_PAGES = ("docs/superpowers/previews/", "docs/superpowers/tools/", "data/", "pipelines/", "schemas/")
LABEL = "muda-a-tela"


def touches_pages(changed):
    return [f for f in changed if f.startswith(BUILDS_PAGES)]


def changed_files(pr, base_sha):
    out = subprocess.run(["git", "-C", str(pr), "diff", "--name-only", f"{base_sha}...HEAD"], capture_output=True, text=True, check=True)
    return [f for f in out.stdout.splitlines() if f]


def pages_of(tree):
    spec = importlib.util.spec_from_file_location("site_chrome_" + tree.name, tree / "docs/superpowers/tools/site_chrome.py")
    sys.path.insert(0, str(tree / "docs/superpowers/tools"))
    try:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        sys.path.pop(0)
    return {key: ("index.html" if key == "inicio" else name) for key, (name, _) in mod.ALL_PAGES.items()}


def serve(folder):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(folder))
    handler.log_message = lambda *a: None
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}/"


def texts_of(tree, out_dir, probe):
    site = out_dir / "site"
    subprocess.run([sys.executable, str(tree / "docs/superpowers/tools/build-site.py"), "--profile", "production", "--out", str(site)],
                   check=True, cwd=tree, stdout=subprocess.DEVNULL)
    server, url = serve(site)
    try:
        texts = {}
        for key, file in pages_of(tree).items():
            out = out_dir / f"{key}.json"
            args = ["node", str(probe), url, str(out)] if key == "inicio" else ["node", str(probe), "--page", url + file, str(out)]
            if subprocess.run(args).returncode != 0:
                raise SystemExit(f"visible-text-check: the capture of {key} failed ({tree.name})")
            texts.update({f"{key}:{k}": v for k, v in json.loads(out.read_text(encoding="utf-8"))["texts"].items()})
        return texts
    finally:
        server.shutdown()


def differences(a, b):
    """The keys whose text differs, each with its first differing line on both sides."""
    out = []
    for k in sorted(set(a) | set(b)):
        if a.get(k) != b.get(k):
            x, y = (a[k].split("\n") if k in a else []), (b[k].split("\n") if k in b else [])
            i = next((n for n in range(max(len(x), len(y))) if (x[n] if n < len(x) else None) != (y[n] if n < len(y) else None)), 0)
            out.append((k, i + 1, x[i] if i < len(x) else "<nada>", y[i] if i < len(y) else "<nada>"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, type=Path)
    ap.add_argument("--pr", required=True, type=Path)
    ap.add_argument("--base-sha", required=True)
    ap.add_argument("--label", action="store_true")
    a = ap.parse_args()
    touched = touches_pages(changed_files(a.pr, a.base_sha))
    if not touched:
        print("visible-text: nothing that builds the pages changed; nothing to compare")
        return 0
    print(f"visible-text: {len(touched)} files build the pages, e.g. {', '.join(touched[:5])}")
    probe = a.pr / "docs/superpowers/tools/visible-text-probe.cjs"
    with tempfile.TemporaryDirectory() as tmp:
        base = texts_of(a.base.resolve(), Path(tmp) / "base", probe)
        pr = texts_of(a.pr.resolve(), Path(tmp) / "pr", probe)
    diff = differences(base, pr)
    print(f"visible-text: {len(set(base) | set(pr))} texts compared, {len(diff)} differ")
    for k, line, x, y in diff[:20]:
        print(f"  {k}, line {line}\n    base: {x[:160]}\n    pull request: {y[:160]}")
    if diff and a.label:
        print(f"visible-text: the screen changes, and the pull request carries the label {LABEL}: passes")
        return 0
    if diff:
        print(f"visible-text: the screen changes; the maintainer adds the label {LABEL} when the change is wanted")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
