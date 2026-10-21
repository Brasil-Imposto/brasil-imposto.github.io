#!/bin/bash
# Scan TCE-SC Diario Oficial Eletronico (DOTC-e) issues between two dates for bridge mentions.
# Usage: dotc_scan.sh <start YYYY-MM-DD> <end YYYY-MM-DD> <outdir>
out="$3"; mkdir -p "$out"
python3 -c "
import datetime,sys
d=datetime.date.fromisoformat('$1'); e=datetime.date.fromisoformat('$2')
while d<=e:
    if d.weekday()<5: print(d.isoformat())
    d+=datetime.timedelta(days=1)" | while read d; do
  f="$out/dotc-e$d.pdf"
  curl -sS -m 90 -o "$f" "https://consulta.tce.sc.gov.br/Diario/dotc-e$d.pdf"
  if file -b "$f" | grep -q PDF; then
    pdftotext -layout "$f" "$out/dotc-e$d.txt"; rm -f "$f"
    n=$(grep -ciE 'Herc.?lio Luz|PJ.?0*56/2016|CT.?0*06/2019|15/00524643' "$out/dotc-e$d.txt")
    echo "$d $n"
  else
    rm -f "$f"; echo "$d notpdf"
  fi
done
