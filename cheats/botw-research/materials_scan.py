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

mgr=u64(base+0x2ca6d48);checked(mgr,0x44000);buf=raw(mgr,0x44000);items=[]
for off in range(0,len(buf)-0x90,8):
 a=mgr+off
 typ=int.from_bytes(buf[off+0x18:off+0x1c],'little',signed=True)
 if typ!=7 or buf[off+0x25]!=1:continue
 if int.from_bytes(buf[off+0x30:off+0x38],'little')!=a+0x3c:continue
 qty=int.from_bytes(buf[off+0x20:off+0x24],'little',signed=True)
 try:name=buf[off+0x3c:off+0x7c].split(b'\0')[0].decode('ascii')
 except UnicodeDecodeError:continue
 if not name or not 1<=qty<=999:continue
 items.append({'object':a,'name':name,'quantity':qty,'offset':hex(off)})
rec={'pid':p.GetProcessID(),'base':base,'manager':mgr,'items':items}
(root/'materials-scan.json').write_text(json.dumps(rec,indent=2));print(json.dumps(rec))
