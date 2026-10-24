#!/usr/bin/env python3
# NSO → ELF64 (AArch64, ET_DYN)：解压 text/ro/data 三段按内存布局拼成镜像，加 PT_LOAD×3 与 PT_DYNAMIC（来自 MOD0）。
# 镜像放在文件偏移 0x1000 起，vaddr 从 0 开始，所以 main+X 就是 ELF 里的地址 X（Ghidra 若改基址，按基址加偏移换算）。
# 用法: nso2elf.py <nso> <out.elf>；依赖 lz4（Splatoon3 venv 里有）。
import struct, sys, lz4.block

d = open(sys.argv[1], 'rb').read()
if d[:4] != b'NSO0': raise SystemExit('不是 NSO')
flags = struct.unpack_from('<I', d, 0xC)[0]
segs = []
for i in range(3):
    foff, moff, size = struct.unpack_from('<III', d, 0x10 + 0x10 * i)
    csize = struct.unpack_from('<I', d, 0x60 + 4 * i)[0]
    raw = d[foff:foff + csize]
    data = lz4.block.decompress(raw, uncompressed_size=size) if flags & (1 << i) else raw
    if len(data) != size: raise SystemExit(f'段 {i} 解压长度不符')
    segs.append((moff, data))
bss = struct.unpack_from('<I', d, 0x3C)[0]
end = segs[2][0] + len(segs[2][1])
img = bytearray(end)
for moff, data in segs: img[moff:moff + len(data)] = data
mod0 = struct.unpack_from('<I', img, 4)[0]
if img[mod0:mod0 + 4] != b'MOD0': raise SystemExit('找不到 MOD0')
dyn = mod0 + struct.unpack_from('<i', img, mod0 + 4)[0]
dynsz = 0
while True:   # 数到 DT_NULL
    tag = struct.unpack_from('<q', img, dyn + dynsz)[0]; dynsz += 16
    if tag == 0: break

BASE = 0x1000
phdrs = []
def load(i, pflags, memsz_extra=0):
    moff, data = segs[i]
    phdrs.append(struct.pack('<IIQQQQQQ', 1, pflags, BASE + moff, moff, moff, len(data), len(data) + memsz_extra, 0x1000))
load(0, 5); load(1, 4); load(2, 6, bss)
phdrs.append(struct.pack('<IIQQQQQQ', 2, 6, BASE + dyn, dyn, dyn, dynsz, dynsz, 8))
ehdr = b'\x7fELF' + bytes([2, 1, 1, 0]) + bytes(8) + struct.pack('<HHIQQQIHHHHHH', 3, 183, 1, 0, 64, 0, 0, 64, 56, len(phdrs), 64, 0, 0)
out = bytearray(BASE + len(img))
out[:len(ehdr)] = ehdr
out[64:64 + 56 * len(phdrs)] = b''.join(phdrs)
out[BASE:] = img
open(sys.argv[2], 'wb').write(out)
print(f'text {len(segs[0][1]):#x} ro {len(segs[1][1]):#x} data {len(segs[2][1]):#x} bss {bss:#x} dynamic @{dyn:#x} ({dynsz} 字节)')
