# Local, bounded LLDB experiment. Never reuse saved addresses across processes.
import lldb,struct,json,os,time
from pathlib import Path
root=Path('/Volumes/SwitchNative/Tools/BotW-cheats160')
p=lldb.debugger.GetSelectedTarget().GetProcess();t=p.GetTarget()
assert t.GetExecutable().fullpath=='/Volumes/SwitchNative/Apps/Breath of the Wild.app/Contents/Resources/totk/build/totk-native'
assert p.GetState()==lldb.eStateStopped

def raw(a,n):
 e=lldb.SBError();b=p.ReadMemory(a,n,e)
 assert e.Success() and len(b)==n,str(e)
 return b

def u64(a):return int.from_bytes(raw(a,8),'little')
def sym(n):
 s=t.FindSymbols(n).GetContextAtIndex(0).GetSymbol();assert s.IsValid(),n
 return s.GetStartAddress().GetLoadAddress(t)
m=sym('modules');base=u64(m+168);heap=u64(sym('heap'));hs=u64(sym('heap_size'))
assert raw(u64(m),5)==b'main\0'
assert raw(u64(m+8),64).decode()=='c41ac2fa9be737f2e6b0ab641508e9a51995b03463ff6aa445ce04e5e8766a8e'
def checked(a,n):
 assert heap<=a and a+n<=heap+hs,'outside guest heap'
 r=lldb.SBMemoryRegionInfo();assert p.GetMemoryRegionInfo(a,r).Success()
 assert r.IsReadable() and r.IsWritable() and not r.IsExecutable() and a+n<=r.GetRegionEnd()
 return raw(a,n)

def item(o):
 q=u64(base+0x2ca6d48);checked(q+o,8);v=u64(q+o);checked(v,0x90)
 name=checked(v+0x3c,64).split(b'\0')[0].decode('ascii')
 assert name.startswith('Weapon_'),name
 return v,name

def put(a,b):
 checked(a,len(b));e=lldb.SBError();assert p.WriteMemory(a,b,e)==len(b) and e.Success(),str(e)
 assert raw(a,len(b))==b

allowed=['最大心心','无限神兽技能','当前箭999，进入装备界面回满','移动速度x4','当前武器变成： 999 精灵','当前武器变成： 999 巨大的古代核心']
case=os.environ['BOTW_NEXT_CASE']; mode=os.environ.get('BOTW_NEXT_MODE','apply'); label=os.environ['BOTW_NEXT_LABEL']
assert case in allowed and label.replace('-','').isalnum()
journal=root/('next-'+label+'.json')
code=next(x['instructions'] for x in json.loads((root/'instruction-audit.json').read_text()) if x['name']==case)
a=None; writes=[]
for words in code:
 op=int(words[0],16)
 if op==0x580f0000:a=u64(base+int(words[1],16))
 elif op==0x580f1000:
  checked(a+int(words[1],16),8);a=u64(a+int(words[1],16))
 elif op==0x780f0000:a+=int(words[1],16)
 elif op in (0x610f0000,0x620f0000,0x640f0000):
  n=(op>>24)&15; val=(int(words[1],16)<<32)|int(words[2],16)
  if os.environ.get('BOTW_ARROW_CONTROL')=='1':
   assert case=='当前箭999，进入装备界面回满'; val=99
  writes.append({'address':a,'before':checked(a,n).hex(),'after':val.to_bytes(n,'little').hex()})
 else:raise ValueError('unsupported opcode')
assert 0<len(writes)<=10
if mode=='apply':
 assert not journal.exists()
 rec={'case':case,'pid':p.GetProcessID(),'base':base,'writes':writes,'status':'prepared'}
 journal.write_text(json.dumps(rec,ensure_ascii=False,indent=2))
 try:
  for w in writes:put(w['address'],bytes.fromhex(w['after']))
 except Exception:
  for w in writes:put(w['address'],bytes.fromhex(w['before']))
  raise
 rec['status']='applied'
elif mode=='restore':
 rec=json.loads(journal.read_text());assert rec['pid']==p.GetProcessID() and rec['base']==base and rec['status']=='applied'
 assert [w['address'] for w in writes]==[w['address'] for w in rec['writes']],'target moved'
 for w in rec['writes']:put(w['address'],bytes.fromhex(w['before']))
 rec['status']='restored'
else:raise ValueError('unknown mode')
journal.write_text(json.dumps(rec,ensure_ascii=False,indent=2));print(json.dumps(rec,ensure_ascii=False))
