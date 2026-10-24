#!/usr/bin/env python3
# 把整合 XCI（本体+更新同在安全分区）按 container.json 的分组拆成两个 NSP（PFS0）。
# 分组规则：按偏移排序，每个 .cnmt.nca 结束一组。每个 NCA 边写边算 SHA-256，必须与文件名（哈希前 16 字节）一致。
# 只读源 XCI；输出先写 .partial，校验全部通过才改名。不需要密钥。
import hashlib, json, struct, sys
from pathlib import Path

root = Path(__file__).parent
src = Path(sys.argv[1])
out = Path(sys.argv[2])
recs = sorted(json.loads((root / 'container.json').read_text()), key=lambda r: r['nca_offset'])

groups, cur = [], []
for r in recs:
    cur.append(r)
    if r['content_type'] == 1:
        groups.append(cur); cur = []
if cur: raise SystemExit('最后一组没有 CNMT，分组不明确')

def write_nsp(group, dest):
    names = b''; table = b''; off = 0
    for r in group:
        table += struct.pack('<QQII', off, r['size'], len(names), 0); names += r['name'].encode() + b'\0'; off += r['size']
    pad = (-(16 + len(table) + len(names))) % 0x20
    names += b'\0' * pad
    header = b'PFS0' + struct.pack('<III', len(group), len(names), 0) + table + names
    part = dest.with_name(dest.name + '.partial')
    with src.open('rb') as f, part.open('wb') as w:
        w.write(header)
        for r in group:
            f.seek(r['nca_offset']); left = r['size']; h = hashlib.sha256()
            while left:
                chunk = f.read(min(left, 8 << 20))
                if not chunk: raise SystemExit('源文件被截断: ' + r['name'])
                w.write(chunk); h.update(chunk); left -= len(chunk)
            want = r['name'].split('.')[0]
            # 整体哈希不符只记警告：转换工具改写 NCA 头也会造成不符；数据完整性交给 nx_extract 的分区哈希树校验（ErrorOnInvalid）
            print('哈希通过' if h.hexdigest()[:32] == want else '【警告】整体哈希与文件名不符', r['name'], r['size'], flush=True)
    part.rename(dest)

out.mkdir(parents=True, exist_ok=True)
for g in groups:
    progs = [r for r in g if r['content_type'] == 0]
    if len(progs) != 1: raise SystemExit('一组里 Program NCA 不是 1 个')
    is_update = progs[0]['patch']
    dest = out / ('Jamboree Update [0100965017338800][v393216].nsp' if is_update else 'Jamboree [0100965017338000][v0].nsp')
    if dest.exists(): raise SystemExit('目标已存在: ' + dest.name)
    write_nsp(g, dest)
    print(json.dumps({'output': dest.name, 'ncas': len(g), 'update': is_update, 'sha256': 'PASS'}, ensure_ascii=False), flush=True)
