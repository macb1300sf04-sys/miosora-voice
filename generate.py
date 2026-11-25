import json, urllib.request, urllib.parse, pathlib, wave, time, sys
BASE="http://127.0.0.1:50021"
def request(path, data=None):
    req=urllib.request.Request(BASE+path,data=data,headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=180) as r: return r.read()
for i in range(120):
    try:
        speakers=json.loads(request("/speakers"))
        break
    except Exception:
        time.sleep(2)
else: raise RuntimeError("VOICEVOX engine unavailable")
ids={}
for role,name in [("Mio","四国めたん"),("Sora","夜語トバリ")]:
    speaker=next(s for s in speakers if s["name"]==name)
    ids[role]=next(s["id"] for s in speaker["styles"] if s["name"]=="ノーマル")
lines=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
out=pathlib.Path("audio"); out.mkdir(exist_ok=True)
manifest=[]
for i,line in enumerate(lines,1):
    role=line["role"]; text=line["text"]; sid=ids[role]
    query=request("/audio_query?"+urllib.parse.urlencode({"text":text,"speaker":sid}),b"")
    wav=request("/synthesis?"+urllib.parse.urlencode({"speaker":sid}),query)
    p=out/f"{i:03d}_{role}.wav"; p.write_bytes(wav)
    with wave.open(str(p)) as w:
        duration=w.getnframes()/w.getframerate()
        assert duration>0
        manifest.append({"file":p.name,"role":role,"seconds":duration,"speaker":sid})
(out/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(manifest,ensure_ascii=False))
