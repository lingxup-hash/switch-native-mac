#!/usr/bin/env python3
# 把整合 XCI 里指定的一组 NCA 写成一个 NSP（PFS0）。用法: split_groups.py <xci> <container.json> <组号> <输出 nsp>
# 边写边算 SHA-256，与文件名（哈希前 16 字节）比对；不符只记警告（转换工具改写 NCA 头也会不符），数据完整性交给 nx_extract 的分区哈希树校验。
# 只读源 XCI；先写 .partial，写完再改名。不需要密钥。
import hashlib, json, struct, sys
from pathlib import Path

src, recs, grp, dest = Path(sys.argv[1]), json.loads(Path(sys.argv[2]).read_text()), int(sys.argv[3]), Path(sys.argv[4])
group = [r for r in recs if r['group'] == grp]
if not group: raise SystemExit('没有这一组')
if dest.exists(): raise SystemExit('目标已存在: ' + dest.name)
names = b''; table = b''; off = 0
for r in group:
    table += struct.pack('<QQII', off, r['size'], len(names), 0); names += r['name'].encode() + b'\0'; off += r['size']
names += b'\0' * ((-(16 + len(table) + len(names))) % 0x20)
header = b'PFS0' + struct.pack('<III', len(group), len(names), 0) + table + names
part = dest.with_name(dest.name + '.partial'); bad = 0
with src.open('rb') as f, part.open('wb') as w:
    w.write(header)
    for r in group:
        f.seek(r['nca_offset']); left = r['size']; h = hashlib.sha256()
        while left:
            chunk = f.read(min(left, 8 << 20))
            if not chunk: raise SystemExit('源文件被截断: ' + r['name'])
            w.write(chunk); h.update(chunk); left -= len(chunk)
        ok = h.hexdigest()[:32] == r['name'].split('.')[0]; bad += not ok
        print('哈希通过' if ok else '【警告】整体哈希与文件名不符', r['name'], r['size'], flush=True)
part.rename(dest)
print(f'完成 {dest.name}：{len(group)} 个 NCA，哈希不符 {bad} 个', flush=True)
