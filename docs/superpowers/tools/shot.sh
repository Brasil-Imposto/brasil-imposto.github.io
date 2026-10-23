#!/bin/zsh
# Screenshot (or probe dump) of a preview through tools/action-probe.html.
# Needs a server: cd docs/superpowers && python3 -m http.server 8765 --bind 127.0.0.1
# usage: CHROME_HEADLESS=<chrome-headless-shell> PAGE=<preview.html[?query], default the published home> shot.sh <width> <height> <out.png|dump> "<probe query, e.g. open=SC&mun=4205407&scrollto=.mun-panel>"
# A fresh browser profile per run (a reused one served stale JS); WebGL needs the swiftshader flags.
S=${SCRATCH:-${TMPDIR:-/tmp}}
HS=${CHROME_HEADLESS:?set CHROME_HEADLESS to a chrome-headless-shell binary, as for the probes}
DOC="http://127.0.0.1:8765/previews/${PAGE:-BRASIL-IMPOSTO_DESIGN_platform-preview_2026-10-09.html}"
ENC=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$DOC")
URL="http://127.0.0.1:8765/tools/action-probe.html?src=$ENC&w=$1&h=$2&$4"
PROF=$(mktemp -d "$S/hsp.XXXX")
FLAGS=(--headless --no-sandbox --enable-unsafe-swiftshader --use-angle=swiftshader --hide-scrollbars --user-data-dir="$PROF" --window-size=$1,$2 --virtual-time-budget=25000)
if [[ "$3" == "dump" ]]; then
  "$HS" "${FLAGS[@]}" --dump-dom "$URL" 2>/dev/null | grep -o 'PROBE [^<]*' | head -1
else
  "$HS" "${FLAGS[@]}" --screenshot="$3" "$URL" >/dev/null 2>&1; echo "shot $3 $?"
fi
rm -rf "$PROF"
