
import os
import requests, time, pathlib, subprocess
BASE="http://RYZEN2.local:1234"; TOK=os.environ.get("LMSTUDIO_TOKEN","")
H={"Authorization": f"Bearer {TOK}", "Content-Type":"application/json"}
W=pathlib.Path("/home/rafaelfrequiao/projects/zeebo-hle-wiki")
Z=pathlib.Path("/home/rafaelfrequiao/projects/zeebo-emulator/research/sources/zeebulator/core")
E=pathlib.Path("/home/rafaelfrequiao/projects/zeebo-emulator/research/sources/zeemu")
def files(d, pat="*.h"):
    try:
        r = subprocess.run(["ls",str(d)],capture_output=True,text=True,timeout=10)
        return r.stdout.strip()
    except Exception as e: return str(e)
def head(fp, n=60):
    try: return "\n".join(pathlib.Path(fp).read_text(errors="replace").splitlines()[:n])
    except Exception as e: return str(e)
JOBS=[
 ("f3-ishell", f"FILES:\n{files(Z/'brew')}\n\nishell.h head:\n{head(Z/'brew/ishell.h')}", "Enumere os slots/funcoes de IShell implementados vs stub. So enumeracao literal + fonte."),
 ("f3-idisplay-file", f"idisplay.h:\n{head(Z/'brew/idisplay.h')}\nfile_hle.h:\n{head(Z/'brew/file_hle.h')}", "Enumere funcoes de IDisplay e IFileMgr/IFile implementadas. So literal + fonte."),
 ("f4-hid", f"hid_hle.h:\n{head(Z/'brew/hid_hle.h')}\nzeemu BrewHID/HIDDevice:\n{files(E/'brew')}", "Enumere o que existe de IHID/HIDDevice nos dois. So literal + fonte."),
 ("f5-video", f"gl_hle.h:\n{head(Z/'brew/gl_hle.h')}\nzeemu GL:\n{head(E/'brew/BrewGL.h')}", "Enumere funcoes GLES implementadas nos dois. So literal + fonte."),
 ("f6-audio", f"media_hle.h:\n{head(Z/'brew/media_hle.h')}", "Enumere funcoes Media/Sound implementadas. So literal + fonte."),
]
def chat(user_, mt=1200):
    r=requests.post(BASE+"/v1/chat/completions",headers=H,json={"model":"lfm2.5-8b-a1b","messages":[{"role":"user","content":user_}],"max_tokens":mt,"temperature":0.0},timeout=150)
    j=r.json(); return j["choices"][0]["message"].get("content","")
log=W/"logs.md"
for cid, ctx, q in JOBS:
    print(f"START {cid}", flush=True)
    t0=time.time()
    try:
        c = chat(f"{ctx[:1500]}\n\nTAREFA: {q}\nTermine com `Resposta: <lista> | <fonte>`.")
        log.write_text(log.read_text()+f"\n## {cid} ({time.time()-t0:.0f}s)\n{c[:1500]}\n")
        print(f"OK {cid} {time.time()-t0:.0f}s", flush=True)
    except Exception as e:
        log.write_text(log.read_text()+f"\n## {cid} ERRO: {e}\n")
        print(f"ERR {cid} {e}", flush=True)
print("F3-F6 ENUM DONE")
