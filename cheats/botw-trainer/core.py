# One-shot, fixed-function BOTW 1.6.0 operations. No arbitrary addresses from UI.
CASES={
 'health':dict(root=0x2ca1a78,chain=[0x80],writes=[(0x848,1,120)],group='health'),
 'rupees':dict(root=0x2cc5fe0,chain=[0xe40,0x5b08],writes=[(0x5d90,4,999999)],group='rupees'),
 'arrows':dict(root=0x2ca6d48,chain=[0x447e8],writes=[(0x20,2,999)],group='arrows'),
 'weapon_dur':dict(root=0x2ca6d48,chain=[0x447d8],writes=[(0x20,4,0x9999999)],group='weapon_dur'),
 'bow_dur':dict(root=0x2ca6d48,chain=[0x447e0],writes=[(0x20,4,0x9999999)],group='bow_dur'),
 'shield_dur':dict(root=0x2ca6d48,chain=[0x447f0],writes=[(0x20,4,0x9999999)],group='shield_dur'),
 'weapon_attack':dict(root=0x2ca6d48,chain=[0x447d8],writes=[(0x80,4,999),(0x88,4,0x80000001)],group='weapon_attack'),
 'shield_boost':dict(root=0x2ca6d48,chain=[0x447f0],writes=[(0x80,4,999),(0x88,4,0x80000181)],group='shield_boost'),
}
for k,v,flags in [('bow_attack',999,0x80000001),('bow_fast_attack',10000,0x80000041),('bow_fast',10000,0x80000040),('bow_five',5,0x80000011)]:
 CASES[k]=dict(root=0x2ca6d48,chain=[0x447e0],writes=[(0x80,4,v),(0x88,4,flags)],group='bow_effect')
def plan(code,base,read_pointer):
 if code not in CASES:raise ValueError('未知功能')
 c=CASES[code];a=read_pointer(base+c['root'])
 if a<0x1000:raise ValueError('目标未就绪，请载入存档并打开背包')
 for off in c['chain']:
  a=read_pointer(a+off)
  if a<0x1000:raise ValueError('目标未就绪，请载入存档并打开背包')
 return [(a+off,v.to_bytes(n,'little')) for off,n,v in c['writes']]

def require_restore_records(records):
 if not records:raise ValueError('当前游戏进程没有可恢复记录；未修改任何数值')
 return records.values()

def atomic_backup(source,destination):
 import shutil,uuid
 from pathlib import Path
 destination=Path(destination)
 if destination.exists():return
 temporary=destination.with_name(destination.name+'.partial-'+uuid.uuid4().hex)
 try:
  shutil.copytree(source,temporary)
  temporary.rename(destination)
 except Exception:
  if temporary.exists():shutil.rmtree(temporary)
  raise

CASES['materials']={'group':'materials'}
def material_entries(data,base):
 import struct,re
 result=[]
 for off in range(0,len(data)-0x90,8):
  if struct.unpack_from('<i',data,off+0x18)[0]!=7 or data[off+0x25]!=1:continue
  if struct.unpack_from('<Q',data,off+0x30)[0]!=base+off+0x3c:continue
  qty=struct.unpack_from('<i',data,off+0x20)[0]
  if not 1<=qty<=999:continue
  b=data[off+0x3c:off+0x7c].split(b'\0')[0]
  if not re.fullmatch(rb'[A-Za-z][A-Za-z0-9_]{1,62}',b):continue
  result.append((base+off,b.decode('ascii'),qty))
 if len(result)>500 or len({x[1] for x in result})!=len(result):raise ValueError('材料结构不一致，已取消')
 if len(result)>1 and len({a%0x298 for a,n,q in result})!=1:raise ValueError('材料布局不一致，已取消')
 return result

ARROW_NAMES={'NormalArrow','FireArrow','IceArrow','ElectricArrow','BombArrow_A','AncientArrow'}
def record_key(code,identity):
 return 'arrows:'+identity if code=='arrows' else CASES[code]['group']
def migrate_arrow_records(records):
 old=records.get('arrows')
 if old:
  key=record_key('arrows',old['identity'])
  if key in records:raise ValueError('箭恢复记录冲突，已取消')
  records[key]=records.pop('arrows')
def arrow_entries(data,base):
 import struct
 result=[]
 for off in range(0,len(data)-0x90,8):
  if struct.unpack_from('<i',data,off+0x18)[0]!=2 or data[off+0x25]!=1:continue
  if struct.unpack_from('<Q',data,off+0x30)[0]!=base+off+0x3c:continue
  qty=struct.unpack_from('<i',data,off+0x20)[0]
  if not 0<=qty<=999:continue
  name=bytes(data[off+0x3c:off+0x7c]).split(b'\0')[0].decode('ascii',errors='replace')
  if name in ARROW_NAMES:result.append((base+off,name,qty))
 if len(result)>6 or len({n for a,n,q in result})!=len(result):raise ValueError('箭背包结构不一致，已取消')
 return result
