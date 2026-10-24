import lldb,struct,json,os
from pathlib import Path
p=lldb.debugger.GetSelectedTarget().GetProcess();t=p.GetTarget()
assert str(t.GetExecutable().fullpath)=='/Volumes/SwitchNative/Apps/Breath of the Wild.app/Contents/Resources/totk/build/totk-native'
def rd(a,n):
 e=lldb.SBError();b=p.ReadMemory(a,n,e)
 assert e.Success() and len(b)==n,str(e)
 return b
def u64(a):return struct.unpack('<Q',rd(a,8))[0]
def sym(n):
 s=t.FindSymbols(n).GetContextAtIndex(0).GetSymbol();assert s.IsValid(),n
 return s.GetStartAddress().GetLoadAddress(t)
m=sym('modules');assert rd(u64(m),5)==b'main\0'
base=u64(m+168)
a=u64(u64(base+0x2c9fd70)+0x38)+0x2ac
heap=u64(sym('heap'));size=u64(sym('heap_size'))
assert heap<=a and a+8<=heap+size,(hex(heap),hex(size),hex(a))
r=lldb.SBMemoryRegionInfo();assert p.GetMemoryRegionInfo(a,r).Success()
assert r.IsWritable() and not r.IsExecutable() and a+8<=r.GetRegionEnd()
old=struct.unpack('<Q',rd(a,8))[0]
restore=os.environ.get('BOTW_STAMINA_RESTORE')=='1'
expected,new=(0x447a0000447a0000,0x453b8000453b8000) if restore else (0x453b8000453b8000,0x447a0000447a0000)
assert old==expected,(old,expected)
e=lldb.SBError();assert p.WriteMemory(a,struct.pack('<Q',new),e)==8 and e.Success()
assert struct.unpack('<Q',rd(a,8))[0]==new
record=dict(pid=p.GetProcessID(),address=hex(a),before=old,after=new,restore=restore,scope='stamina parameter control 1000 vs 3000; not infinite proof')
with open('/Volumes/SwitchNative/Tools/BotW-cheats160/stamina-test.jsonl','a') as f:f.write(json.dumps(record)+'\n')
print(record)
