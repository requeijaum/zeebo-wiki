
import os
import requests, time, pathlib, subprocess
BASE="http://RYZEN2.local:1234"; TOK=os.environ.get("LMSTUDIO_TOKEN","")
H={"Authorization": f"Bearer {TOK}", "Content-Type":"application/json"}
W=pathlib.Path("/home/rafaelfrequiao/projects/zeebo-hle-wiki")
def relevant(fp, keys, ctx=3, cap=1800):
    try:
        r = subprocess.run(["grep","-i","-m","12",f"-C{ctx}","--", "|".join(keys), fp],capture_output=True,text=True,timeout=15)
        out = r.stdout.strip() or pathlib.Path(fp).read_text()[:cap]
        return out[:cap]
    except Exception as e:
        return pathlib.Path(fp).read_text()[:cap]
SRC="/home/rafaelfrequiao/projects/zeebo-emulator/research/sources"
ZDX="/home/rafaelfrequiao/projects/zeebx-emu/docs/02-plataforma-brew.md"
ABI="/home/rafaelfrequiao/projects/zeebo-emulator/docs/brew-abi.md"
REC="/home/rafaelfrequiao/projects/brew-sim-recon/README.md"
CELLS=[
 ("loader-zeebulator", SRC+"/zeebulator.md", ["GGZ","BAR","MIF","\\.mod","loader"], "Como o Zeebulator carrega GGZ/BAR/MIF/.mod? 2 frases + arquivo-fonte."),
 ("brew-zeebulator", SRC+"/zeebulator.md", ["core/brew","ishell","idisplay","media_hle","hid_hle","file_hle"], "Quais modulos BREW o Zeebulator implementa? Liste nomes + fonte."),
 ("brew-zeemu", SRC+"/2026-08-31_zeebulator-vs-zeemu-hle-coverage.md", ["Brew","interface","module"], "Quais interfaces BREW o Zeemu cobre? Liste 10 + fonte."),
 ("infuse-status", SRC+"/infuse.md", ["playable","menu","Double Dragon","Crash"], "Quais jogos Zeebo o Infuse roda jogavel vs so menu? Liste + fonte."),
 ("oem-zwheel", SRC+"/2026-08-31_zeebulator-vs-zeemu-hle-coverage.md", ["ZWheel","OEM","HID"], "O que se sabe de Z-Wheel/OEM Zeebo? 2 frases + fonte."),
 ("ggz-formato", SRC+"/MANIFEST.md", ["ggzbrewtools","GGZ","pack"], "O que e ggzbrewtools e o que prova sobre GGZ? 2 frases + fonte."),
 ("zeeno-status", SRC+"/zeeno.md", ["Zeeno","Qt","open source","status"], "Status do Zeeno? 2 frases + fonte."),
 ("runtime-brew", ZDX, ["AEEMod_Load","CreateInstance","HandleEvent","SetTimer"], "Ciclo de vida BREW: load, create, event, timer. 3 frases + fonte."),
 ("abi-eventos", ABI, ["EVT_APP_START","AEERect","AEEAppStart"], "Valores EVT_APP_START/STOP e tamanhos AEERect/AEEAppStart? Exato + fonte."),
 ("sdk-headers", REC, ["AEE.*\\.h","sdk-extract","contrato"], "Quais headers AEE sao contrato primario e onde? Liste + fonte."),
]
def chat(user_, mt=2000):
    r=requests.post(BASE+"/v1/chat/completions",headers=H,json={"model":"lfm2.5-8b-a1b","messages":[{"role":"user","content":user_}],"max_tokens":mt,"temperature":0.0},timeout=150)
    j=r.json(); m=j["choices"][0]["message"]
    return m.get("content",""), j.get("usage",{})
log=W/"logs.md"
for cid, fp, keys, q in CELLS:
    print(f"START {cid}", flush=True)
    ctx=relevant(fp, keys)
    t0=time.time()
    try:
        c, u = chat(f"FONTE ({fp}, trechos relevantes):\n{ctx}\n\nExtraia fato literal. Termine com `Resposta: <fato> | <fonte>`.\nPERGUNTA: {q}")
        log.write_text(log.read_text()+f"\n## {cid} ({time.time()-t0:.0f}s)\n{c[:1500]}\n")
        print(f"OK {cid} {time.time()-t0:.0f}s", flush=True)
    except Exception as e:
        log.write_text(log.read_text()+f"\n## {cid} ERRO: {e}\n")
        print(f"ERR {cid} {e}", flush=True)
print("F0 DONE")
