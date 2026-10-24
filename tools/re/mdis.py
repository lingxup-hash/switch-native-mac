#!/usr/bin/env python3
# 反汇编 main.elf 的一段，bl 目标标注 PLT 导入名。用法: dis.py <elf> <起> <止> [自动找函数起点:1]
import sys,struct; sys.path.insert(0,'/Volumes/SwitchNative/Tools/MarioPartyJamboree/rea')
from elfsyms import Elf
from capstone import *
e=Elf(sys.argv[1]); img=e.img; md=Cs(CS_ARCH_ARM64,CS_MODE_ARM)
jm={}
for k in range(e.tags[2]//24):
  off,info,_=struct.unpack_from('<QQq',img,e.tags[23]+24*k); jm[off]=e.syms[(info>>32)-1][0]
def plt(t):
  w=struct.unpack_from('<I',img,t)[0]; w2=struct.unpack_from('<I',img,t+4)[0]
  if (w&0x9f000000)!=0x90000000: return None
  immlo,immhi=(w>>29)&3,(w>>5)&0x7ffff; imm=(immhi<<2)|immlo
  if imm>>20: imm-=1<<21
  page=(t&~0xfff)+(imm<<12)
  return jm.get(page+((w2>>10)&0xfff)*8) if (w2&0xffc00000)==0xf9400000 else None
a,b=int(sys.argv[2],16),int(sys.argv[3],16)
if len(sys.argv)>4:
  while a>0:
    w=struct.unpack_from('<I',img,a)[0]
    if (w&0xffc003ff)==0xa98003fd or (w&0xff8003ff)==0xd10003ff: break
    a-=4
for i in md.disasm(img[a:b],a):
  s='%#x  %-6s %s'%(i.address,i.mnemonic,i.op_str)
  if i.mnemonic in('bl','b') and i.op_str.startswith('#0x'):
    n=plt(int(i.op_str[1:],16)); s+=('    ; '+n[:90]) if n else ''
  print(s)
