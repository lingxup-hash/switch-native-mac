from pathlib import Path
import sys,struct,io,hashlib,json
sys.path.insert(0,'/Volumes/SwitchNative/Projects/MacNativeGames/games/totk/scripts')
from extract_exefs import *
source=Path('/Volumes/T7 Shield/[0100F2C0115B6000] [v393216] (1G+1U).nsp')
out=Path('/Volumes/SwitchNative/GameFiles/TOTK/update-1.2.1/TOTK-update-1.2.1.nsp')
assert not out.exists()
keys=load_keys(Path('/Volumes/T7 Shield/prod.keys'))
with source.open('rb') as f:
 kind,entries=container_entries(f,source.stat().st_size)
 records=nca_inventory(f,entries,keys);tickets=common_tickets(f,entries)
 record,hdr=next((r,h) for r,h in records if r['title_id']=='0100F2C0115B6800' and r['content_type']==1)
 key=nca_ctr_key(hdr,keys,tickets)
 fs=hdr[0x400:0x600];start,end=struct.unpack_from('<II',hdr,0x240)
 assert hashlib.sha256(fs).digest()==hdr[0x280:0x2a0] and fs[2:5]==bytes([1,2,3])
 def read(rel,size):
  absolute=start*512+rel;aligned=absolute&~15
  iv=fs[0x140:0x148][::-1]+(aligned//16).to_bytes(8,'big')
  return decrypt(key,modes.CTR(iv),read_at(f,record['nca_offset']+aligned,size+absolute-aligned))[absolute-aligned:]
 block,levels=struct.unpack_from('<II',fs,0x28)
 ho,hs,po,ps=struct.unpack_from('<QQQQ',fs,0x30)
 hashes=read(ho,hs);data=read(po,ps)
 assert levels==2 and hashlib.sha256(hashes).digest()==fs[8:40]
 for i,pos in enumerate(range(0,ps,block)):assert hashlib.sha256(data[pos:pos+block]).digest()==hashes[i*32:(i+1)*32]
 n,off,size=next(x for x in partition_entries(io.BytesIO(data),0,len(data)) if x[0].endswith('.cnmt'))
 cnmt=data[off:off+size]
 title,version=struct.unpack_from('<QI',cnmt)
 ext,count=struct.unpack_from('<HH',cnmt,0xE)
 assert title==0x0100F2C0115B6800 and version==393216
 wanted={record['name']};expected={}
 for i in range(count):
  item=cnmt[0x20+ext+i*0x38:0x20+ext+(i+1)*0x38]
  if item[54]==6: continue  # Delta fragments are not required to apply the cumulative Program NCA.
  name=item[32:48].hex()+'.nca';wanted.add(name);expected[name]=item[:32].hex()
 selected=[e for e in entries if e[0] in wanted or e[0].endswith(('.tik','.cert'))]
 assert wanted<={e[0] for e in selected}, f'Missing entries: {wanted-{e[0] for e in selected}}; available: {[e[0] for e in entries]}'
 strings=b'';table=b'';offset=0
 for name,src_off,length in selected:
  table+=struct.pack('<QQII',offset,length,len(strings),0);strings+=name.encode()+b'\0';offset+=length
 padding=(-16-len(table)-len(strings))%16;strings+=bytes(padding)
 partial=out.with_suffix('.partial')
 with partial.open('xb') as dst:
  dst.write(b'PFS0'+struct.pack('<III',len(selected),len(strings),0)+table+strings)
  for name,src_off,length in selected:
   f.seek(src_off);h=hashlib.sha256();remaining=length
   while remaining:
    b=f.read(min(8<<20,remaining));assert b;dst.write(b);h.update(b);remaining-=len(b)
   if name in expected:assert h.hexdigest()==expected[name],f'CNMT hash mismatch: {name}'
 partial.rename(out)
 print(json.dumps({'output':str(out),'title':f'{title:016X}','version':version,'content_ncas_verified':len(expected),'entries':len(selected)}))
