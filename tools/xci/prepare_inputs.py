import json,struct,subprocess,hashlib
from pathlib import Path
root=Path(__file__).parent
src=Path('/Volumes/T7 Shield/Super Mario Party Jamboree [0100965017338000] [v393216] (1G+1U).xci')
records=json.loads((root/'container.json').read_text()); byname={r['name']:r for r in records}
out=Path('/Volumes/SwitchNative/GameFiles/MarioPartyJamboree')
with src.open('rb') as f:
 for meta in [r for r in records if r['content_type']==1]:
  p=root/meta['name']; f.seek(meta['nca_offset']);p.write_bytes(f.read(meta['size']))
  unpack=root/(meta['name']+'.unpacked')
  result=subprocess.run(['/Volumes/SwitchNative/Builds/BotW/src/hactool/hactool','-x','-k','/Volumes/T7 Shield/prod.keys','--section0dir='+str(unpack),str(p)],capture_output=True)
  cnmts=list(unpack.glob('*.cnmt'))
  if len(cnmts)!=1:raise RuntimeError('Metadata extraction failed')
  raw=cnmts[0].read_bytes();tid,ver=struct.unpack_from('<QI',raw);ext,count=struct.unpack_from('<HH',raw,0xe)
  group=[meta]; expected={}
  for i in range(count):
   q=raw[0x20+ext+i*0x38:0x20+ext+(i+1)*0x38];name=q[0x20:0x30].hex()+'.nca'
   if name not in byname:raise RuntimeError('Missing content '+name)
   r=byname[name];assert r['size']==int.from_bytes(q[0x30:0x36],'little');group.append(r);expected[name]=q[:32].hex()
  dest=out/f'Jamboree [{tid:016X}][v{ver}].nsp'
  if dest.exists():raise RuntimeError('Destination exists')
  names=b'';table=b'';offset=0
  for r in group:
   table+=struct.pack('<QQII',offset,r['size'],len(names),0);names+=r['name'].encode()+b'\0';offset+=r['size']
  header=b'PFS0'+struct.pack('<III',len(group),len(names),0)+table+names
  with dest.with_suffix('.partial').open('wb') as w:
   w.write(header)
   for r in group:
    f.seek(r['nca_offset']);left=r['size'];h=hashlib.sha256()
    while left:
     chunk=f.read(min(left,8*1024*1024))
     if not chunk:raise RuntimeError('Truncated source')
     w.write(chunk);h.update(chunk);left-=len(chunk)
    if r['name'] in expected and h.hexdigest()!=expected[r['name']]:raise RuntimeError('Content SHA256 mismatch: '+r['name'])
  dest.with_suffix('.partial').rename(dest)
  print(json.dumps({'title_id':f'{tid:016X}','version':ver,'ncas':len(group),'content_sha256':'PASS','output':str(dest)}),flush=True)
