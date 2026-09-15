
import requests, time, pathlib
BASE="http://RYZEN2.local:1234"
import os
TOK=os.environ.get("LMSTUDIO_TOKEN","")
H={"Authorization": f"Bearer {TOK}", "Content-Type":"application/json"}
W=pathlib.Path("/home/rafaelfrequiao/projects/zeebo-wiki")
O=pathlib.Path("/tmp/tec_en"); O.mkdir(exist_ok=True)
def chunks(t, cap=1000):
    out, cur = [], []
    n = 0
    for ln in t.splitlines():
        cur.append(ln); n += len(ln)
        if n >= cap and not ln.strip().startswith("|"):
            out.append("\n".join(cur)); cur=[]; n=0
    if cur: out.append("\n".join(cur))
    return out
def chat(user_, mt=1500, extra=0):
    mt = 2200 if extra else mt
    r=requests.post(BASE+"/v1/chat/completions",headers=H,json={"model":"lfm2.5-8b-a1b","messages":[{"role":"user","content":user_}],"max_tokens":mt,"temperature":0.0},timeout=180)
    return r.json()["choices"][0]["message"].get("content","")
SYS="Translate Brazilian Portuguese technical prose to English. Keep markdown structure, tables, code, numbers, badge tags ([CONF],[INCERTO],[ATENÇÃO],[PRIOR-ART]), URLs and file paths EXACTLY. Output only the translation."
for fn in ["TEC-pcsx2-dolphin.md","TEC-ymir-ares-higan.md","TEC-prior-art.md"]:
    ch = chunks((W/fn).read_text())
    print(f"{fn}: {len(ch)} chunks", flush=True)
    for i, c in enumerate(ch):
        dest = O/f"{fn}.part{i}"
        if dest.exists() and dest.stat().st_size > 50:
            print(f"skip {fn}#{i}", flush=True); continue
        print(f"START {fn}#{i}", flush=True)
        t0=time.time()
        try:
            r = chat(SYS+"\n\n"+c)
            if len(r) < 50:
                r = chat(SYS+"\n\nTranslate. Output ONLY English.\n\n"+c, extra=1)
            dest.write_text(r)
            print(f"OK {fn}#{i} {time.time()-t0:.0f}s len={len(r)}", flush=True)
        except Exception as e:
            print(f"ERR {fn}#{i} {e}", flush=True)
print("TEC-EN DONE")
