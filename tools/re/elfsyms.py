#!/usr/bin/env python3
# nso2elf.py 转出的 ELF 的小工具：符号表、RELATIVE/ABS 重定位，用于还原虚函数表。
import struct

class Elf:
    def __init__(s, path):
        f = open(path, 'rb').read(); s.img = f[0x1000:]
        ph = [struct.unpack_from('<IIQQQQQQ', f, 64 + 56 * i) for i in range(struct.unpack_from('<H', f, 56)[0])]
        s.text_end = ph[0][5]
        dyn = next(p[3] for p in ph if p[0] == 2); tags = {}; o = dyn
        while True:
            t, v = struct.unpack_from('<qQ', s.img, o); o += 16
            if t == 0: break
            tags.setdefault(t, v)
        s.tags = tags
        symtab, strtab = tags[6], tags[5]
        s.syms = []   # (name, value, size, defined)
        for i in range(1, (strtab - symtab) // 24):
            st, info, other, shndx, val, size = struct.unpack_from('<IBBHQQ', s.img, symtab + 24 * i)
            nm = s.img[strtab + st:s.img.index(b'\0', strtab + st)].decode('latin1')
            s.syms.append((nm, val, size, shndx != 0))
        s.by_addr = {}
        for nm, val, size, d in s.syms:
            if d and val: s.by_addr.setdefault(val, nm)
        s.rel = {}    # 地址 → ('rel', 目标) 或 ('sym', 名字)
        if 7 in tags:
            for k in range(tags[8] // 24):
                off, info, add = struct.unpack_from('<QQq', s.img, tags[7] + 24 * k)
                typ, si = info & 0xffffffff, info >> 32
                if typ == 1027: s.rel[off] = ('rel', add)
                elif typ in (257, 1025, 1026): s.rel[off] = ('sym', s.syms[si - 1][0])
        if 0x24 in tags:   # DT_RELR（0x24 地址，0x23 大小）
            a = 0; base = tags[0x24]
            for k in range(tags[0x23] // 8):
                e = struct.unpack_from('<Q', s.img, base + 8 * k)[0]
                if not e & 1:
                    a = e; s.rel[a] = ('rel', struct.unpack_from('<Q', s.img, a)[0]); a += 8
                else:
                    for j in range(63):
                        if (e >> (j + 1)) & 1: x = a + 8 * j; s.rel[x] = ('rel', struct.unpack_from('<Q', s.img, x)[0])
                    a += 8 * 63
    def sym(s, name):
        return next(((v, z) for n, v, z, d in s.syms if n == name and d), None)
    def q(s, a): return struct.unpack_from('<Q', s.img, a)[0]
