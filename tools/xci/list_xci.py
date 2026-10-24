#!/usr/bin/env python3
# 列出 XCI 安全分区（secure HFS0）里的文件：名称、绝对偏移、大小。只读，不需要密钥。
import json, struct, sys

def hfs0(f, base):
    f.seek(base); h = f.read(16)
    if h[:4] != b'HFS0': raise SystemExit(f'@{base:#x} 不是 HFS0')
    n, strsz = struct.unpack_from('<II', h, 4)
    ents = f.read(n * 0x40); strs = f.read(strsz)
    data = base + 16 + n * 0x40 + strsz
    out = []
    for i in range(n):
        off, size, noff = struct.unpack_from('<QQI', ents, i * 0x40)
        name = strs[noff:strs.index(b'\0', noff)].decode()
        out.append({'name': name, 'offset': data + off, 'size': size})
    return out

with open(sys.argv[1], 'rb') as f:
    f.seek(0x100)
    if f.read(4) != b'HEAD': raise SystemExit('不是 XCI')
    f.seek(0x130); root = struct.unpack('<Q', f.read(8))[0]
    parts = {p['name']: p for p in hfs0(f, root)}
    sec = hfs0(f, parts['secure']['offset'])
print(json.dumps(sorted(sec, key=lambda r: r['offset']), indent=1))
