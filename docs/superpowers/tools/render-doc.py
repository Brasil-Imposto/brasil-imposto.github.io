#!/usr/bin/env python3
"""Render a spec, plan or research markdown file into an HTML review copy in the Brasil-Imposto identity.
The markdown stays canonical; the HTML is the review artifact and opens from its file path.
The theme is the project's own (light paper, Manrope, ink, green, red, yellow).

Usage: render-doc.py <in.md> <out.html> [--kind spec]
A line "@@include name.svg" places that file (next to the markdown) inline, as a figure."""
import re, sys, html, pathlib, datetime

INCLUDE_DIR = pathlib.Path(".")  # folder of the markdown being rendered (set in main)
FONT_LINK = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
             '<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">')

CSS = r"""
  :root { --ink:#14202B; --ink2:#3C4A57; --muted:#5B6773; --faint:#8A95A1; --line:#E3E7EC; --paper:#FFFFFF; --soft:#F6F8FA;
          --green:#12803F; --green-soft:#EFF7F1; --red:#B41E25; --yellow:#E0A100; --yellow-soft:#FFF8E6; --yellow-ink:#6B5310; }
  * { margin:0; padding:0; box-sizing:border-box; }
  html { background:var(--soft); }
  body { font-variant-ligatures:no-common-ligatures; background:var(--soft); color:var(--ink); font-family:'Manrope',system-ui,sans-serif; font-size:16px; line-height:1.55; -webkit-font-smoothing:antialiased; }
  .page { max-width:1120px; margin:0 auto; padding:26px 32px 56px; }
  .page p, .page li { overflow-wrap:break-word; }
  .figure { background:var(--paper); border:1px solid var(--line); border-radius:14px; padding:12px; margin:16px 0 6px; overflow-x:auto; }
  .figure svg { display:block; width:100%; min-width:760px; height:auto; }
  .topbar { display:flex; align-items:center; justify-content:space-between; gap:16px; padding-bottom:16px; border-bottom:1px solid var(--line); }
  .wordmark { display:flex; align-items:center; gap:10px; font-weight:800; letter-spacing:-.01em; font-size:16px; }
  .wordmark i { font-style:normal; color:var(--faint); }
  .wm-flag { width:28px; height:20px; object-fit:cover; border-radius:4px; box-shadow:0 0 0 1px rgba(20,32,43,.14); }
  .eyebrow { font-size:11px; font-weight:700; letter-spacing:.14em; text-transform:uppercase; color:var(--muted); }
  .topbar .eyebrow { text-align:right; }
  h1 { font-size:clamp(24px,2.6vw,36px); line-height:1.1; letter-spacing:-.025em; margin:26px 0 10px; font-weight:800; }
  .status { display:inline-block; font-size:11px; font-weight:800; letter-spacing:.12em; text-transform:uppercase; padding:5px 10px; border-radius:999px;
            background:var(--yellow-soft); color:var(--yellow-ink); box-shadow:inset 0 0 0 1px #F1DFA8; margin:2px 0 14px; }
  .lead { font-size:15.5px; color:var(--ink2); max-width:88ch; margin:0 0 10px; }
  .intro { background:var(--paper); border:1px solid var(--line); border-radius:14px; padding:18px 22px; margin:14px 0 6px; }
  .intro h3 { margin-top:0; }
  .frame { background:var(--paper); border:1px solid var(--line); border-radius:14px; padding:20px 24px 14px; margin-top:16px; box-shadow:0 1px 2px rgba(20,32,43,.04); }
  .frame h2 { font-size:clamp(17px,1.6vw,21px); font-weight:800; letter-spacing:-.015em; line-height:1.25; display:flex; align-items:baseline; gap:12px; }
  .frame h2 .no { font-size:11px; font-weight:800; letter-spacing:.14em; color:var(--green); background:var(--green-soft); border-radius:6px; padding:3px 7px; flex:none; }
  .rule { height:3px; width:44px; border-radius:2px; background:var(--green); margin:10px 0 14px; }
  h3 { font-size:11px; font-weight:800; letter-spacing:.14em; text-transform:uppercase; color:var(--muted); margin:18px 0 8px; }
  p { color:var(--ink2); font-size:15px; line-height:1.6; margin:0 0 10px; max-width:96ch; }
  p b, li b, td b { color:var(--ink); font-weight:800; }
  ul, ol { margin:0 0 10px 0; list-style:none; }
  ol { counter-reset:n; }
  li { position:relative; padding-left:22px; font-size:15px; line-height:1.55; color:var(--ink2); margin-bottom:7px; }
  ul li::before { content:""; position:absolute; left:4px; top:.62em; width:7px; height:7px; border-radius:50%; background:var(--green); }
  ol li { padding-left:30px; }
  ol li::before { content:counter(n); counter-increment:n; position:absolute; left:0; top:.1em; width:21px; height:21px; border-radius:50%; background:var(--green-soft);
                  color:var(--green); font-size:11.5px; font-weight:800; display:flex; align-items:center; justify-content:center; }
  code { font-family:ui-monospace,'SFMono-Regular',Menlo,monospace; font-size:.84em; color:var(--ink); background:var(--soft); padding:1px 5px; border-radius:5px; border:1px solid var(--line); overflow-wrap:anywhere; }
  pre { font-family:ui-monospace,'SFMono-Regular',Menlo,monospace; font-size:12.5px; line-height:1.55; color:var(--ink2); background:var(--soft); border:1px solid var(--line); border-radius:10px; padding:14px 16px; overflow-x:auto; margin:8px 0 12px; }
  pre code { background:none; border:0; padding:0; font-size:inherit; color:inherit; overflow-wrap:normal; }
  .tscroll { overflow-x:auto; margin:6px 0 12px; }
  table { width:100%; border-collapse:collapse; font-size:14px; line-height:1.45; }
  th { text-align:left; padding:0 10px 8px; font-size:10.5px; font-weight:800; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); border-bottom:2px solid var(--line); }
  td { padding:9px 10px; color:var(--ink2); border-bottom:1px solid var(--line); vertical-align:top; }
  tr:last-child td { border-bottom:0; }
  td:first-child { color:var(--ink); font-weight:700; }
  a { color:var(--green); text-decoration:underline; text-decoration-color:rgba(18,128,63,.35); }
  hr { border:0; height:1px; background:var(--line); margin:16px 0; }
  blockquote { margin:10px 0 12px; padding:2px 0 2px 14px; border-left:3px solid var(--yellow); }
  blockquote p { font-style:italic; margin:0 0 6px; }
  .bar code.path { text-transform:none; letter-spacing:0; font-weight:600; }
  .bar { margin-top:26px; padding-top:12px; display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:10px 24px; border-top:1px solid var(--line); }
  @media (min-width:900px) { td.key { white-space:nowrap; } }
  @media (max-width:899px) { .page { padding:18px 16px 44px; } .frame, .intro { padding:16px 14px 10px; } .topbar { flex-wrap:wrap; } .topbar .eyebrow { text-align:left; } table { font-size:13.5px; }
    pre { white-space:pre-wrap; overflow-wrap:anywhere; }
    table, tbody, tr, td { display:block; width:100%; } thead { display:none; }
    tr { padding:10px 0; border-bottom:1px solid var(--line); } tr:last-child { border-bottom:0; }
    td { border:0; padding:2px 0; overflow-wrap:anywhere; } td:first-child { font-size:14.5px; }
    td[data-label]::before { content:attr(data-label); display:block; font-size:10px; font-weight:800; letter-spacing:.1em; text-transform:uppercase; color:var(--faint); margin-top:4px; } }
"""

TOPBAR = ('<div class="wordmark"><img class="wm-flag" src="assets/flags/br.svg" alt="Bandeira do Brasil"><span>Brasil<i>·</i>Imposto</span></div>'
          '<div class="eyebrow">{kind} · {today}</div>')
FOOTER = ('<span class="eyebrow">Brasil·Imposto · {kind}</span>'
          '<span class="eyebrow">Canônico: o markdown em <code class="path">{src}</code></span>')


def inline(t):
    t = html.escape(t, quote=False)
    spans = []
    def keep(m):
        spans.append(f"<code>{m.group(1)}</code>"); return f"\x00{len(spans) - 1}\x00"
    t = re.sub(r"`([^`]+)`", keep, t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"<i>\1</i>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    return re.sub(r"\x00(\d+)\x00", lambda m: spans[int(m.group(1))], t)


def render(md: str, kind: str, src: str):
    lines = md.splitlines()
    title = "Sem título"; status = ""; out = []; i = 0; sec_open = False; n_sec = 0; intro_open = False
    def close_sec():
        nonlocal sec_open
        if sec_open: out.append("</div>"); sec_open = False
    def close_intro():
        nonlocal intro_open
        if intro_open: out.append("</div>"); intro_open = False
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("# "):
            title = inline(ln[2:].strip()); i += 1; continue
        if ln.startswith("## "):
            close_intro(); close_sec(); n_sec += 1
            h = inline(ln[3:].strip()); h = re.sub(r"^(\d+)\.\s*", "", h)
            out.append(f'<div class="frame"><h2><span class="no">{n_sec:02d}</span><span>{h}</span></h2><div class="rule"></div>'); sec_open = True; i += 1; continue
        if ln.startswith("### "):
            if n_sec == 0 and not intro_open:
                out.append('<div class="intro">'); intro_open = True
            out.append(f"<h3>{inline(ln[4:].strip())}</h3>"); i += 1; continue
        if ln.startswith("```"):
            j = i + 1; buf = []
            while j < len(lines) and not lines[j].startswith("```"): buf.append(lines[j]); j += 1
            out.append("<pre><code>" + html.escape("\n".join(buf)) + "</code></pre>"); i = j + 1; continue
        if ln.startswith("@@include "):
            out.append('<div class="figure">' + (INCLUDE_DIR / ln.split(None, 1)[1].strip()).read_text(encoding="utf-8") + "</div>"); i += 1; continue
        if ln.strip() == "---": out.append("<hr>"); i += 1; continue
        if ln.startswith(">"):
            quoted = []
            while i < len(lines) and lines[i].startswith(">"):
                quoted.append(re.sub(r"^>\s?", "", lines[i])); i += 1
            paras, cur = [], []
            for q in quoted:
                if q.strip(): cur.append(q.strip())
                elif cur: paras.append(" ".join(cur)); cur = []
            if cur: paras.append(" ".join(cur))
            out.append("<blockquote>" + "".join(f"<p>{inline(x)}</p>" for x in paras) + "</blockquote>")
            continue
        if ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"): rows.append(lines[i]); i += 1
            cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
            if len(cells) >= 2 and all(re.fullmatch(r":?-{2,}:?", c) for c in cells[1]):
                head, body = cells[0], cells[2:]
            else:
                head, body = None, cells
            t = '<div class="tscroll"><table>'
            if head: t += "<thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead>"
            def td(k, c):
                short = k == 0 and len(re.sub(r"[`*]", "", c)) <= 28
                label = f' data-label="{html.escape(re.sub(r"[`*]", "", head[k]))}"' if head and k > 0 and k < len(head) else ""
                return f'<td class="key"{label}>{inline(c)}</td>' if short else f"<td{label}>{inline(c)}</td>"
            t += "<tbody>" + "".join("<tr>" + "".join(td(k, c) for k, c in enumerate(r)) + "</tr>" for r in body) + "</tbody></table></div>"
            out.append(t); continue
        m_ul = re.match(r"^\s*[-*]\s+(.*)", ln); m_ol = re.match(r"^\s*\d+\.\s+(.*)", ln)
        if m_ul or m_ol:
            tag = "ul" if m_ul else "ol"; items = []
            while i < len(lines):
                m = re.match(r"^\s*[-*]\s+(.*)", lines[i]) if tag == "ul" else re.match(r"^\s*\d+\.\s+(.*)", lines[i])
                if m:
                    item = m.group(1); i += 1
                    while i < len(lines) and lines[i].startswith("  ") and not re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
                        item += " " + lines[i].strip(); i += 1
                    items.append(item)
                else: break
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>"); continue
        if ln.strip() == "": i += 1; continue
        buf = [ln.strip()]; i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#|```|\||>|\s*[-*]\s|\s*\d+\.\s|---)", lines[i]): buf.append(lines[i].strip()); i += 1
        para = " ".join(buf)
        m_st = re.match(r"^Status:\s*(.*)", para)
        if m_st and not status:
            raw = m_st.group(1)
            m_b = re.search(r"\*\*(.+?)\*\*", raw)
            status = (m_b.group(1) if m_b else re.split(r"[.(]", raw)[0]).strip(" .")
            out.append(f'<p class="lead">{inline(para)}</p>'); continue
        cls = ' class="lead"' if not sec_open and n_sec == 0 else ""
        out.append(f"<p{cls}>{inline(para)}</p>")
    close_intro(); close_sec()
    today = datetime.date.today().isoformat()
    esc = {"kind": html.escape(kind), "today": today, "src": html.escape(src)}
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{re.sub(r'<[^>]+>', '', title)} · {today}</title>
{FONT_LINK}
<style>{CSS}</style></head>
<body>
<div class="page">
  <header class="topbar">{TOPBAR.format(**esc)}</header>
  <h1>{title}</h1>
  {f'<div class="status">{html.escape(status)}</div>' if status else ''}
  {chr(10).join(out)}
  <footer class="bar">{FOOTER.format(**esc)}</footer>
</div></body></html>
"""


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2: print(__doc__); sys.exit(2)
    src, dst = pathlib.Path(args[0]), pathlib.Path(args[1])
    INCLUDE_DIR = src.resolve().parent
    kind = args[args.index("--kind") + 1] if "--kind" in args else "documento"
    rel = src.resolve().as_posix().split("/docs/", 1)[-1]
    dst.write_text(render(src.read_text(encoding="utf-8"), kind, "docs/" + rel), encoding="utf-8")
    print("wrote", dst, dst.stat().st_size, "bytes")
