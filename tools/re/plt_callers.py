#!/usr/bin/env python3
# 在 nso2elf.py 转出的 ELF 里：按名字找导入符号的 GOT 槽 → 找引用这个槽的 PLT 桩 → 扫 text 段里所有 bl 到桩的调用点。
# 用法: plt_callers.py <elf> <符号子串>...   地址都是模块内偏移（= main+X）。
import struct, sys
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM

f = open(sys.argv[1], 'rb').read(); B = 0x1000; img = f[B:]
ph = [struct.unpack_from('<IIQQQQQQ', f, 64 + 56 * i) for i in range(struct.unpack_from('<H', f, 56)[0])]
text_end = ph[0][5]
dyn = next(p[3] for p in ph if p[0] == 2)
tags = {}
o = dyn
while True:
    t, v = struct.unpack_from('<qQ', img, o); o += 16
    if t == 0: break
    tags.setdefault(t, v)
symtab, strtab, jmprel, pltsz = tags[6], tags[5], tags[23], tags[2]
def name(i):
    st = struct.unpack_from('<I', img, symtab + 24 * i)[0]
    return img[strtab + st:img.index(b'\0', strtab + st)].decode()
got = {}
for k in range(pltsz // 24):
    off, info, _ = struct.unpack_from('<QQq', img, jmprel + 24 * k)
    got[off] = name(info >> 32)
want = {g: n for g, n in got.items() if any(s in n for s in sys.argv[2:])}
md = Cs(CS_ARCH_ARM64, CS_MODE_ARM); md.detail = False
stubs = {}
# PLT 桩形如 adrp x16, page; ldr x17, [x16, #lo]; add x16...; br x17
for a in range(text_end - 0x40000, text_end, 4):
    w = struct.unpack_from('<I', img, a)[0]
    if (w & 0x9f00001f) != 0x90000010: continue   # adrp x16
    immlo, immhi = (w >> 29) & 3, (w >> 5) & 0x7ffff
    page = (a & ~0xfff) + (((immhi << 2) | immlo) << 12 if not (immhi >> 18) else ((((immhi << 2) | immlo) - (1 << 21)) << 12))
    w2 = struct.unpack_from('<I', img, a + 4)[0]
    if (w2 & 0xffc003ff) != 0xf9400211: continue  # ldr x17, [x16, #imm]
    slot = page + ((w2 >> 10) & 0xfff) * 8
    if slot in want: stubs[a] = want[slot]
print('PLT 桩:', {hex(k): v for k, v in stubs.items()})
for a in range(0, text_end, 4):
    w = struct.unpack_from('<I', img, a)[0]
    if (w >> 26) != 0x25: continue                # bl
    imm = w & 0x3ffffff
    t = a + ((imm - (1 << 26)) if imm >> 25 else imm) * 4
    if t in stubs: print(f'main+{a:#x}  bl {stubs[t]}')
