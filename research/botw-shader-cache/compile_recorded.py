import sys, json, hashlib, subprocess, os, time
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,'/Volumes/SwitchNative/Projects/MacNativeGames')
import build_app
root=Path(__file__).parent
out=root/'shader-libs'; out.mkdir(exist_ok=True)
srcdir=root/'sources'; srcdir.mkdir(exist_ok=True)
found=build_app.metal_compiler()
if not found: raise SystemExit('Metal compiler unavailable')
metal,version,env=found
jobs=json.loads((root/'missing-libs.json').read_text())
results=[]
for digest,source in jobs.items():
 raw=Path(source).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=digest: raise SystemExit('Source changed')
 src=srcdir/(digest+'.metal'); src.write_bytes(raw)
 partial=out/(digest+'.partial')
 r=subprocess.run([metal,*build_app.METAL_FLAGS,'-o',str(partial),str(src)],capture_output=True,text=True,env=env)
 if r.returncode==0: partial.replace(out/(digest+'.metallib'))
 results.append({'sha256':digest,'ok':r.returncode==0,'error':r.stderr if r.returncode else ''})
 if len(results)%20==0: print(f'{len(results)}/{len(jobs)}',flush=True)
(root/'compile-results.json').write_text(json.dumps({'compiler':version,'flags':build_app.METAL_FLAGS,'results':results},indent=2))
print(json.dumps({'compiled':sum(x['ok'] for x in results),'failed':sum(not x['ok'] for x in results)}),flush=True)
