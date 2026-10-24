import lldb,struct,json
from pathlib import Path
p=lldb.debugger.GetSelectedTarget().GetProcess();t=p.GetTarget()
def raw(a,n):
 e=lldb.SBError();b=p.ReadMemory(a,n,e)
 if e.Fail() or len(b)!=n:raise ValueError('unreadable '+hex(a))
 return b
def u64(a):return int.from_bytes(raw(a,8),'little')
def sym(n):
 s=t.FindSymbols(n).GetContextAtIndex(0).GetSymbol();assert s.IsValid()
 return s.GetStartAddress().GetLoadAddress(t)
m=sym('modules');base=u64(m+168);size=u64(m+24);heap=u64(sym('heap'));hs=u64(sym('heap_size'))
assert raw(u64(m),5)==b'main\0'
def read(a,n):
 assert (base<=a and a+n<=base+size) or (heap<=a and a+n<=heap+hs),'outside guest range '+hex(a)
 return raw(a,n)
def pointer(a):
 v=int.from_bytes(read(a,8),'little');assert v>=0x1000,'null pointer';return v
out=[]
for c in json.loads(Path('/Volumes/SwitchNative/Tools/BotW-cheats160/instruction-audit.json').read_text()):
 try:
  addr=None;writes=[];conditional=False
  for i in c['instructions']:
   op=int(i[0],16)
   if op==0x580f0000:addr=pointer(base+int(i[1],16))
   elif op==0x580f1000:addr=pointer(addr+int(i[1],16))
   elif op==0x780f0000:addr+=int(i[1],16)
   elif op in (0x610f0000,0x620f0000,0x640f0000,0x680f0000):
    n=(op>>24)&15;v=(int(i[1],16)<<32)|int(i[2],16)
    assert heap<=addr and addr+n<=heap+hs,'write outside guest heap'
    r=lldb.SBMemoryRegionInfo();assert p.GetMemoryRegionInfo(addr,r).Success() and r.IsWritable() and not r.IsExecutable()
    writes.append({'address':hex(addr),'before':read(addr,n).hex(),'after':(v&((1<<(n*8))-1)).to_bytes(n,'little').hex()})
   elif op>>28 in (8,2):conditional=True
   else:raise ValueError('unsupported opcode '+hex(op))
  out.append({'name':c['name'],'conditional':conditional,'writes':writes,'status':'address-only; no writes performed'})
 except Exception as e:out.append({'name':c['name'],'error':str(e)})
Path('/Volumes/SwitchNative/Tools/BotW-cheats160/all-live-addresses.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print('Address resolution:',sum('error' not in c for c in out),'/',len(out))
for c in out:
 if 'error' in c:print(c['name'],c['error'])
