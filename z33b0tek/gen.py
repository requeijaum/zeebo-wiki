
import pathlib, re, html, time
W = pathlib.Path(__file__).parent.parent
OUT = pathlib.Path(__file__).parent / "site"
PAGES = ["F0-matriz.md","F1-loader.md","F2-runtime.md","F3-brew.md","F4-input.md","F4b-oem-zwheel.md",
 "F5-video.md","F6-audio.md","F7-jogos.md","F8-frontends.md","MATRIZ-ALVO-infuse.md","LACUNAS.md",
 "CONFRONTO-fork.md","memory/ABI-conf.md","memory/F0-fatos.md","ESCOPO-NAO.md","AGENTS.md","skill-impact.md","STATUS.md","VTABLE-IShell.md","VTABLE-IDisplay.md","HW-regmap.md","HW-syscalls.md","TEC-pcsx2-dolphin.md","TEC-ymir-ares-higan.md","TEC-prior-art.md","TEC-lessons.md","TEC-cpu.md","INDEX.md"]
TITLES = {"F0-matriz.md":"F0 Coverage Matrix","F1-loader.md":"F1 Loader (GGZ/BAR/MIF/MOD)",
 "F2-runtime.md":"F2 AEE Runtime","F3-brew.md":"F3 Core BREW","F4-input.md":"F4 Input (HID)",
 "F4b-oem-zwheel.md":"F4b OEM Z-Wheel","F5-video.md":"F5 Video (GLES/Raster)",
 "F6-audio.md":"F6 Audio (Media)","F7-jogos.md":"F7 Title Gate","F8-frontends.md":"F8 Frontends",
 "MATRIZ-ALVO-infuse.md":"Target: Infuse Oracle","LACUNAS.md":"Known Gaps",
 "CONFRONTO-fork.md":"Fork confronto (parked)","memory/ABI-conf.md":"ABI Facts",
 "memory/F0-fatos.md":"F0 Facts","ESCOPO-NAO.md":"Non-scope","AGENTS.md":"Conventions",
 "skill-impact.md":"Skill Impact Log","STATUS.md":"Status","VTABLE-IShell.md":"VTable IShell (49 slots)","VTABLE-IDisplay.md":"VTable IDisplay","HW-regmap.md":"HW MSM7201A Regmap (LLE)"}
def inline(s):
    s = html.escape(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\[CONF[^\]]*\]", lambda m: f'<span class="bdg conf">{html.escape(m.group(0))}</span>', s)
    for tag, cls in [("[INCERTO]","unc"),("[EM CURSO]","wip"),("PARKED","unc")]:
        s = s.replace(html.escape(tag), f'<span class="bdg {cls}">{tag}</span>')
    return s
def md2html(text):
    out, lines, i, n2, h2n = [], text.splitlines(), 0, 0, 0
    incode, inul = False, False
    while i < len(lines):
        ln = lines[i]
        if ln.strip().startswith("```"):
            out.append("</ul>" if inul else ""); inul = False
            out.append("<pre><code>" if not incode else "</code></pre>")
            incode = not incode; i += 1; continue
        if incode:
            out.append(html.escape(ln)); i += 1; continue
        if re.match(r"^#{1,3} ", ln):
            if inul: out.append("</ul>"); inul = False
            lv = len(ln.split(" ")[0]); title = inline(ln.strip("# "))
            slug = re.sub(r"[^a-z0-9]+","-",re.sub(r"<[^>]+>","",title).lower()).strip("-")
            if lv == 2: n2 += 1; h2n = 0; out.append(f"<h2 id=\"s{n2}-{slug}\">{n2}. {title}</h2>")
            elif lv == 3: h2n += 1; out.append(f"<h3 id=\"s{n2}-{h2n}-{slug}\">{n2}.{h2n} {title}</h3>")
            else: out.append(f"<p><i>{title}</i></p>")
            i += 1; continue
        if ln.strip().startswith("|") and i+1 < len(lines) and re.match(r"^\|?[\s:\-|]+\|?$", lines[i+1]):
            if inul: out.append("</ul>"); inul = False
            cells = [inline(c.strip()) for c in ln.strip().strip("|").split("|")]
            out.append("<table><tr>" + "".join(f"<th>{c}</th>" for c in cells) + "</tr>")
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [inline(c.strip()) for c in lines[i].strip().strip("|").split("|")]
                out.append("<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
                i += 1
            out.append("</table>"); continue
        if re.match(r"^[-*] ", ln.strip()):
            if not inul: out.append("<ul>"); inul = True
            out.append(f"<li>{inline(re.sub(r'^[-*] ','',ln.strip()))}</li>")
            i += 1; continue
        if not ln.strip():
            if inul: out.append("</ul>"); inul = False
            i += 1; continue
        if inul: out.append("</ul>"); inul = False
        out.append(f"<p>{inline(ln.strip())}</p>"); i += 1
    if inul: out.append("</ul>")
    return "\n".join(out)
CSS = """body{background:#fff;color:#000;font:14px/1.5 Georgia,"Times New Roman",serif;margin:0}
a{color:#00c}a:visited{color:#848}header{background:#000;color:#fff;padding:8px 16px;font-family:Verdana,Arial,sans-serif}header b{color:#ff3}
a{color:#00c}header{background:#222;color:#eee;padding:10px 18px}header b{color:#fc3}
.wrap{display:grid;grid-template-columns:230px 1fr;max-width:1200px;margin:0 auto}
nav{background:#f2f2f2;padding:14px;font-size:13px}nav a{display:block;padding:2px 6px}
main{padding:18px 34px}h1{font-size:22px;border-bottom:2px solid #222}h2{font-size:17px;color:#fff;background:#444;padding:3px 10px}h3{font-size:14px;color:#040;border-bottom:1px solid #484}
table{border-collapse:collapse;margin:10px 0;font-size:13px}th,td{border:1px solid #888;padding:3px 8px;text-align:left}th{background:#ddd}
code{background:#eee;padding:0 4px;font:13px monospace}pre{background:#111;color:#0d0;padding:10px;font:13px monospace;overflow-x:auto}pre code{background:none;color:#0d0}
.bdg{font:700 11px monospace;padding:0 5px;border-radius:3px}.conf{background:#dfd;color:#060;border:1px solid #060}.unc{background:#fed;color:#830;border:1px solid #830}.wip{background:#ddf;color:#009;border:1px solid #009}
footer{font-size:12px;color:#666;border-top:1px solid #999;margin-top:30px;padding-top:6px}
@media(max-width:800px){.wrap{grid-template-columns:1fr}nav{position:static}}"""
(OUT/"style.css").write_text(CSS)
GROUPS = [("Fases",["F0-matriz.md","F1-loader.md","F2-runtime.md","F3-brew.md","F4-input.md","F4b-oem-zwheel.md","F5-video.md","F6-audio.md","F7-jogos.md","F8-frontends.md"]),
 ("HW",["HW-regmap.md","HW-syscalls.md"]),("Tabelas SDK",["VTABLE-IShell.md","VTABLE-IDisplay.md","memory/ABI-conf.md","memory/F0-fatos.md"]),
 ("Alvos",["MATRIZ-ALVO-infuse.md","LACUNAS.md","STATUS.md"]),
 ("TEC",["TEC-lessons.md","TEC-cpu.md","TEC-pcsx2-dolphin.md","TEC-ymir-ares-higan.md","TEC-prior-art.md"]),
 ("Processo",["AGENTS.md","skill-impact.md","ESCOPO-NAO.md","CONFRONTO-fork.md"])]
def _link(p): return f'<a href="{p.replace("/","_").replace(".md",".html")}">{TITLES.get(p,p)}</a>'
nav = "".join(f"<b>{g}</b>" + "".join(_link(p) for p in ps if p in PAGES) for g, ps in GROUPS)
for p in PAGES:
    src = W/p
    if not src.exists(): continue
    body = md2html(src.read_text())
    toc = "".join(f'<br><a href="#{m.group(1)}">{m.group(2)}</a>' for m in re.finditer(r"<h2 id=\"([^\"]+)\">(.*?)</h2>", body))
    if toc: body = "<p><b>Contents:</b>" + toc + "</p><hr>" + body
    fn = p.replace("/","_").replace(".md",".html")
    title = TITLES.get(p,p)
    (OUT/fn).write_text(f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>z33b0tek - {title}</title><link rel="stylesheet" href="style.css"></head><body><header><b>z33b0tek</b> Zeebo HLE Technical Reference (from zeebo-hle-wiki markdown)</header><div class="wrap"><nav><a href="index.html">Index</a>{nav}</nav><main><h1>{title}</h1>{body}<footer>src: zeebo-hle-wiki/{p} | generated, wiki is truth</footer></main></div></body></html>""")
idx = "".join(f"<h2>{g}</h2><ul>" + "".join(f'<li><a href="{p.replace("/","_").replace(".md",".html")}">{TITLES.get(p,p)}</a></li>' for p in ps if p in PAGES) + "</ul>" for g, ps in GROUPS)
(OUT/"index.html").write_text(f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>z33b0tek - Index</title><link rel="stylesheet" href="style.css"></head><body><header><b>z33b0tek</b> Zeebo HLE Technical Reference</header><div class="wrap"><nav><a href="index.html">Index</a>{nav}</nav><main><h1>Index</h1><p>Generated from <code>zeebo-hle-wiki/*.md</code>. Markdown is truth; HTML is view.</p><ul>{idx}</ul></main></div></body></html>""")
STAMP = time.strftime("%Y-%m-%d %H:%M")
for f in OUT.glob("*.html"):
    h = f.read_text(); f.write_text(h.replace("generated, wiki is truth", f"generated {STAMP}, wiki is truth"))
print("built", len(list(OUT.glob("*.html"))), "pages", STAMP)
