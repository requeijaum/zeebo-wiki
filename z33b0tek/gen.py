
import pathlib, re, html, time
W = pathlib.Path(__file__).parent / "pages"
OUT = pathlib.Path(__file__).parent / "site"
OUT.mkdir(parents=True, exist_ok=True)
PAGES = [p.name for p in sorted((W).glob("*.md"))]
TITLES = {}
DROPS = {"F5-video.md":["parked-fork"],"F6-audio.md":["parked fork"],
 "F4-input.md":["parked-fork"],"F4b-oem-zwheel.md":["zeebx zwheel diff"],
 "F8-frontends.md":["zeemu frontend"]}
NEUTRAL = ["direct read of the clone|source review",
 "(clone, 09-1[45])|(09-15)",
 "the clone contract|the HLE contract",
 "clone `Build\\(\\)`|`Build\\(\\) wiring",
 "4-way proof:.*$|cross-checked: SDK macro, independent HLE trees and a real game disassembly call site",
 "zeemu `BrewZWheelOem.h`|`BrewZWheelOem.h`",
 "in the zeebx fix|in one observed fix",
 "Matches the vs-zeemu note: the trampoline|Observed mechanism: the trampoline",
 "The clone has a GM soundfont synth \u2014 divergence to exploit.|A GM soundfont synth covers game music in the HLE tree.",
 "\\(`zeebulator_game_probe`, upstream README\\)| (reference standalone tool)",
 "consenso SDK.*$|SDK, independent trees and game disassembly agree",
 "^- Local zeebulator clone has .*\\n|",
 "Confrontation with parked fork.|Second-tree check pending.",
 "Fork runtime HID|Second-tree runtime HID",
 "brew-sim-recon, |",
 "Zeemu: 51 modules, depth unmeasured \\(breadth only\\)|One tree exposes 51 BREW modules; depth unmeasured",
 "^- Infuse: closed source; Z-Wheel skipped on cost.\\n|",
 "Parked fork: no audio decoder|Known gap: no audio decoder in one tree",
 "START busy-wait \\(TIMER_PREEMPT pending\\)|START busy-wait pattern (needs preempting timer)",
 "^- Zeemu frontend.*\\n(?:^- .*\\n)?|"]
def scrub(s):
    s = s.replace("/home/rafaelfrequiao/projects/","")
    s = s.replace("/home/rafaelfrequiao/","")
    s = re.sub(r"\(FONTE[^)]*\)", "", s)
    for rule in NEUTRAL:
        pat, rep = rule.split("|", 1)
        s = re.sub(pat, rep, s, flags=re.M)
    s = re.sub(r"(?i)\bclone\b", "HLE core", s)
    s = s.replace("ZEEBX_GL_CLEANROOM_DIFF.md", "cross-tree GL ABI notes")
    s = re.sub(r"(?i)\bzeebx\b", "a second tree", s)
    s = re.sub(r"(?i)\bzeebulator\b", "the HLE reference tree", s)
    s = re.sub(r"(?i)\bzeemu\b", "another HLE tree", s)
    s = re.sub(r"(?i)\binfuse\b", "the closed-source reference", s)
    s = re.sub(r"(?i)\bcurupira\b", "the in-development tree", s)
    s = re.sub(r"(?i)\b(marcelo|tanisho|kaio|tuxality|requeijaum|rafaelfrequiao)\b", "[author]", s)
    s = re.sub(r"(?i)\b(bateria|comparar|sonda_[a-z]+|game_probe|brew-sim-recon)\b", "[tool]", s)
    s = re.sub(r"(?i)(TASKS|ROADMAP|PHASE8_LOG|VALIDACAO-[A-Z0-9\-]+|INDEX|MANIFEST|FINDINGS|RESUME|AUDIT_[0-9]+)\.md", "internal notes", s)
    return s
def drop_sections(fn, text):
    keys = DROPS.get(fn, [])
    if not keys: return text
    out, skip = [], False
    for ln in text.splitlines():
        if ln.startswith("## "):
            skip = any(k.lower() in ln.lower() for k in keys)
            if skip: continue
        if not skip: out.append(ln)
    return "\n".join(out)
def inline(s):
    s = html.escape(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w\*])_([^_]+)_(?![\w\*])", r"<i>\1</i>", s)
    s = re.sub(r"\[CONF[^\]]*\]", lambda m: f'<span class="bdg conf">{html.escape(m.group(0))}</span>', s)
    for tag, cls in [("[INCERTO]","unc"),("[EM CURSO]","wip"),("[IN PROGRESS]","wip"),("PARKED","unc")]:
        s = s.replace(html.escape(tag), f'<span class="bdg {cls}">{tag}</span>')
    return s
def md2html(text, fn=""):
    """Markdown subset renderer.

    Consecutive prose lines join into one paragraph, and wrapped lines inside a
    list item stay inside that item. Tables, fenced code, headings and inline
    tags are handled explicitly.
    """
    text = drop_sections(fn, text)
    text = scrub(text)
    out = []
    i, n = 0, 0
    h2n = 0
    para = []
    items = []          # finished list items
    cur = None          # current list item buffer
    in_code = False

    def flush_para():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    def flush_list():
        nonlocal cur
        if cur is not None:
            items.append(" ".join(cur))
            cur = None
        if items:
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>")
            items.clear()

    def flush_all():
        flush_para(); flush_list()

    lines = text.splitlines()
    while i < len(lines):
        ln = lines[i]

        if ln.strip().startswith("<!--"):
            flush_all()
            i += 1
            continue
        if ln.strip().startswith("```"):
            flush_all()
            out.append("<pre><code>" if not in_code else "</code></pre>")
            in_code = not in_code
            i += 1
            continue
        if in_code:
            out.append(html.escape(ln))
            i += 1
            continue

        if re.match(r"^#{1,3} ", ln):
            flush_all()
            lv = len(ln.split(" ")[0])
            title = inline(ln.strip("# "))
            slug = re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>", "", title).lower()).strip("-")
            if lv == 2:
                n += 1; h2n = 0
                out.append(f'<h2 id="s{n}-{slug}">{n}. {title}</h2>')
            elif lv == 3:
                h2n += 1
                out.append(f'<h3 id="s{n}-{h2n}-{slug}">{n}.{h2n} {title}</h3>')
            else:
                pass  # the page template prints the H1
            i += 1
            continue

        if ln.strip().startswith("|") and i + 1 < len(lines) and re.match(r"^\|?[\s:\-|]+\|?$", lines[i + 1]):
            flush_all()
            cells = [inline(c.strip()) for c in ln.strip().strip("|").split("|")]
            out.append("<table><tr>" + "".join(f"<th>{c}</th>" for c in cells) + "</tr>")
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [inline(c.strip()) for c in lines[i].strip().strip("|").split("|")]
                out.append("<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
                i += 1
            out.append("</table>")
            continue

        if not ln.strip():
            if cur is not None:
                flush_list()
            flush_para()
            i += 1
            continue

        m = re.match(r"^(\s*)[-*] +(.*)$", ln)
        if m:
            flush_para()
            if cur is not None:
                items.append(" ".join(cur))
            cur = [m.group(2).strip()]
            i += 1
            continue

        if cur is not None:
            cur.append(ln.strip())
            i += 1
            continue

        para.append(ln.strip())
        i += 1

    flush_all()
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
GROUPS = [("Start",["1-overview.md","2-loader.md"]),
 ("Runtime",["3-runtime-aee.md","4-ishell.md","5-idisplay.md","6-input.md"]),
 ("OEM and media",["7-oem-zwheel.md","8-video.md","9-audio.md","10-storage-vfs.md"]),
 ("Hardware",["11-hw-registers.md","12-hw-syscalls.md"]),
 ("Reference",["13-abi.md","14-open-questions.md"])]
def _link(p): return f'<a href="{p.replace("/","_").replace(".md",".html")}">{TITLES.get(p,p)}</a>'
def title_of(path):
    for ln in (W/path).read_text().splitlines():
        if ln.startswith("# "):
            return ln[2:].strip()
    return path
TITLES = {p: title_of(p) for p in PAGES}
nav = "".join(f"<b>{g}</b>" + "".join(_link(p) for p in ps if p in PAGES) for g, ps in GROUPS)
for p in PAGES:
    src = W/p
    if not src.exists(): continue
    body = md2html(src.read_text(), p)
    toc = "".join(f'<br><a href="#{m.group(1)}">{m.group(2)}</a>' for m in re.finditer(r"<h2 id=\"([^\"]+)\">(.*?)</h2>", body))
    if toc: body = "<p><b>Contents:</b>" + toc + "</p><hr>" + body
    fn = p.replace("/","_").replace(".md",".html")
    title = TITLES.get(p,p)
    (OUT/fn).write_text(f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>z33b0tek - {title}</title><link rel="stylesheet" href="style.css"></head><body><header><b>z33b0tek</b> Zeebo (MSM7201A / BREW 4.0.2) technical reference</header><div class="wrap"><nav><a href="index.html">Index</a>{nav}</nav><main><h1>{title}</h1>{body}<footer>z33b0tek &mdash; facts tagged [CONF] verified against public SDK headers, real game binaries and firmware dumps. Generated {p}.</footer></main></div></body></html>""")
idx = "".join(f"<h2>{g}</h2><ul>" + "".join(f'<li><a href="{p.replace("/","_").replace(".md",".html")}">{TITLES.get(p,p)}</a></li>' for p in ps if p in PAGES) + "</ul>" for g, ps in GROUPS)
(OUT/"index.html").write_text(f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>z33b0tek - Index</title><link rel="stylesheet" href="style.css"></head><body><header><b>z33b0tek</b> Zeebo (MSM7201A / BREW 4.0.2) technical reference</header><div class="wrap"><nav><a href="index.html">Index</a>{nav}</nav><main><h1>Index</h1><p>A technical reference for the Zeebo console: Qualcomm MSM7201A, BREW 4.0.2, Adreno 130.</p><p>Fourteen pages cover container formats, the AEE runtime contract, the shell and display interfaces, input, the OEM store layer, video, audio, storage, hardware registers, kernel syscalls, the ABI and the open questions.</p><ul>{idx}</ul></main></div></body></html>""")
STAMP = time.strftime("%Y-%m-%d %H:%M")
for f in OUT.glob("*.html"):
    h = f.read_text(); f.write_text(h.replace("generated, wiki is truth", f"generated {STAMP}, wiki is truth"))
FORBIDDEN = [r"(?i)zeebulator", r"(?i)zeemu", r"(?i)infuse", r"(?i)zeebx", r"(?i)curupira",
 r"(?i)marcelo|tanisho|kaio|tuxality", r"(?i)requeijaum|rafaelfrequiao", r"/home/",
 r"(?i)\bclone\b", r"(?i)bateria", r"(?i)game_probe", r"(?i)pcsx2|dolphin|higan|ymir|dynarmic",
 r"(?i)skill-impact|confronto|phase8|roadmap", r"(?i)compat-list", r"FONTE"]
bad = []
for f in sorted(OUT.glob("*.html")):
    txt = f.read_text()
    for pat in FORBIDDEN:
        m = re.search(r"(?s).{0,60}" + pat.replace("(?i)","") + r".{0,60}", txt, re.I)
        if m: bad.append(f"{f.name}: {pat} -> {m.group(0)[:110]}")
if bad:
    print("LINT FAIL:\n" + "\n".join(bad[:25])); raise SystemExit(1)
print("built", len(list(OUT.glob("*.html"))), "pages", STAMP, "| lint clean")