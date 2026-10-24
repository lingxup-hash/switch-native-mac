import lldb,json,os,sys,time,subprocess
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from core import CASES,plan,require_restore_records,material_entries,arrow_entries,record_key,migrate_arrow_records
req=json.loads(Path(os.environ['BOTW_TRAINER_REQUEST']).read_text())
def run():
 p=lldb.debugger.GetSelectedTarget().GetProcess();t=p.GetTarget()
 if p.GetProcessID()!=req['pid'] or p.GetState()!=lldb.eStateStopped:raise ValueError('游戏状态变化，已取消')
 if subprocess.check_output(['/bin/ps','-p',str(req['pid']),'-o','lstart='],text=True).strip()!=req['start']:raise ValueError('游戏进程已改变')
 if t.GetExecutable().fullpath!='/Volumes/SwitchNative/Apps/Breath of the Wild.app/Contents/Resources/totk/build/totk-native':raise ValueError('游戏不匹配')
 def raw(a,n):
  e=lldb.SBError();b=p.ReadMemory(a,n,e)
  if e.Fail() or len(b)!=n:raise ValueError('目标不可读，请载入存档并打开背包')
  return b
 def u64(a):return int.from_bytes(raw(a,8),'little')
 def sym(n):
  s=t.FindSymbols(n).GetContextAtIndex(0).GetSymbol()
  if not s.IsValid():raise ValueError('原生版本不兼容')
  return s.GetStartAddress().GetLoadAddress(t)
 m=sym('modules');base=u64(m+168);ms=u64(m+24);heap=u64(sym('heap'));hs=u64(sym('heap_size'))
 if raw(u64(m),5)!=b'main\0' or raw(u64(m+8),64).decode()!='c41ac2fa9be737f2e6b0ab641508e9a51995b03463ff6aa445ce04e5e8766a8e':raise ValueError('仅支持已验证的 1.6.0 原生构建')
 def check(a,n,write=False):
  if not(heap<=a and a+n<=heap+hs) and not(not write and base<=a and a+n<=base+ms):raise ValueError('目标地址未就绪；请打开背包')
  r=lldb.SBMemoryRegionInfo()
  if p.GetMemoryRegionInfo(a,r).Fail() or not r.IsReadable() or a+n>r.GetRegionEnd():raise ValueError('目标内存不可读')
  if write and (not r.IsWritable() or r.IsExecutable()):raise ValueError('目标不可修改')
 def ptr(a):check(a,8);return u64(a)
 def writes(code):
  if code=='materials':
   mgr=ptr(base+0x2ca6d48);check(mgr,0x44000)
   entries=material_entries(raw(mgr,0x44000),mgr)
   if not entries:raise ValueError('没有找到已有材料，请载入存档并打开背包')
   ops=[(a+0x20,(999).to_bytes(4,'little')) for a,n,q in entries]
   for a,b in ops:check(a,4,True)
   return ops,[n for a,n,q in entries]
  ops=plan(code,base,ptr)
  for a,b in ops:check(a,len(b),True)
  identity=None
  if CASES[code]['root']==0x2ca6d48:
   obj=ptr(ptr(base+0x2ca6d48)+CASES[code]['chain'][0]);check(obj+0x3c,64)
   identity=raw(obj+0x3c,64).split(b'\0')[0].hex()
   if code=='arrows':
    mgr=ptr(base+0x2ca6d48);check(mgr,0x44000)
    if not any(a==obj and n.encode().hex()==identity for a,n,q in arrow_entries(raw(mgr,0x44000),mgr)):raise ValueError('当前目标不是有效箭种，已取消')
  return ops,identity
 def put(a,b):
  check(a,len(b),True);e=lldb.SBError()
  if p.WriteMemory(a,b,e)!=len(b) or e.Fail() or raw(a,len(b))!=b:raise ValueError('写入失败')
 journal=Path(req['root'])/'session.json'
 state={'pid':req['pid'],'start':req['start'],'base':base,'records':{}}
 if journal.exists():
  saved=json.loads(journal.read_text())
  if all(saved.get(k)==state[k] for k in ('pid','start','base')):state=saved
 migrate_arrow_records(state['records'])
 def persist():
  tmp=journal.with_suffix('.tmp');tmp.write_text(json.dumps(state));tmp.chmod(0o600);tmp.replace(journal)
 if req['action']=='restore':
  changes=[]
  for rec in require_restore_records(state['records']):
   if rec['code']=='arrows':
    mgr=ptr(base+0x2ca6d48);check(mgr,0x44000)
    matches=[a for a,n,q in arrow_entries(raw(mgr,0x44000),mgr) if n.encode().hex()==rec['identity']]
    if len(matches)!=1 or len(rec['values'])!=1:raise ValueError('原箭种不在背包中，无法恢复；未写入任何数值')
    a=matches[0]+0x20;b=bytes.fromhex(rec['values'][0]['before'])
    if len(b)!=2:raise ValueError('箭恢复记录无效')
    check(a,2,True);changes.append((a,b));continue
   ops,ident=writes(rec['code'])
   if ident!=rec['identity'] or [a for a,b in ops]!=[x['address'] for x in rec['values']]:raise ValueError('装备或场景已更换，无法恢复旧目标；请读回备份存档')
   for x in rec['values']:changes.append((x['address'],bytes.fromhex(x['before'])))
  current=[(a,raw(a,len(b))) for a,b in changes]
  try:
   for a,b in changes:put(a,b)
  except Exception:
   for a,b in current:put(a,b)
   raise
  state['records']={};persist();return '已恢复本次修改的原值（不撤销已经保存的存档）'
 code=req['code'];ops,ident=writes(code);group=record_key(code,ident)
 if req['action']=='inspect' and code=='materials':return f'已识别 {len(ops)} 种已有材料；不包含武器、料理和重要物品'
 if req['action']=='inspect':return '目标已就绪，当前原始值：'+', '.join(str(int.from_bytes(raw(a,len(b)),'little')) for a,b in ops)
 current=[{'address':a,'before':raw(a,len(b)).hex(),'after':b.hex()} for a,b in ops]
 old=state['records'].get(group)
 if old and (old['identity']!=ident or [x['address'] for x in old['values']]!=[a for a,b in ops]):raise ValueError('目标已更换，请先恢复或重新启动游戏')
 rec={'code':code,'identity':ident,'values':current}
 if old:
  for x,y in zip(rec['values'],old['values']):x['before']=y['before']
 previous=json.loads(json.dumps(state));state['records'][group]=rec;persist()
 try:
  for a,b in ops:put(a,b)
 except Exception:
  for x in current:put(x['address'],bytes.fromhex(x['before']))
  state=previous;persist();raise
 return '修改成功。装备和数量请关闭背包再打开查看；这是单次修改。'
try:r={'ok':True,'message':run()}
except Exception as e:r={'ok':False,'message':str(e)}
Path(req['result']).write_text(json.dumps(r,ensure_ascii=False))
