"""Read-only NSO/ELF32 inventory; no game code execution or modification."""
import hashlib, json, struct
from pathlib import Path
import lz4.block
import capstone

ROOT = Path('/Volumes/SwitchNative/Builds/Mush8/compat-3.0.3/exefs')
OUT = Path(__file__).parent
def u32(b, off): return struct.unpack_from('<I', b, off)[0]
results = []
for name in ['rtld', 'main', 'subsdk0', 'sdk']:
    raw = (ROOT/name).read_bytes()
    assert raw[:4] == b'NSO0'
    flags = u32(raw, 12)
    segments = []
    for i in range(3):
        off, addr, size = struct.unpack_from('<III', raw, 0x10+i*16)
        compressed = bool(flags & (1 << i))
        n = u32(raw, 0x60+i*4) if compressed else size
        data = raw[off:off+n]
        if compressed: data = lz4.block.decompress(data, uncompressed_size=size)
        assert len(data) == size
        segments.append((addr, data))
    image = bytearray(max(a+len(b) for a,b in segments))
    for a,b in segments: image[a:a+len(b)] = b
    mod = u32(image, 4)
    assert image[mod:mod+4] == b'MOD0'
    dynamic = mod + struct.unpack_from('<i', image, mod+4)[0]
    tags = {}
    for p in range(dynamic, len(image)-7, 8):
        tag,val = struct.unpack_from('<II', image,p)
        if tag == 0: break
        tags[tag] = val
    assert tags.get(11,16) == 16, 'ELF32 symbol size mismatch'
    ro = segments[1][0]
    so, ss, yo, ys = struct.unpack_from('<IIII', raw, 0x90)
    strings = image[ro+so:ro+so+ss]
    symbols = image[ro+yo:ro+yo+ys]
    functions, imports, badnames = [], [], 0
    for p in range(16,len(symbols)-15,16):
        no,value,size,info,other,section = struct.unpack_from('<IIIBBH',symbols,p)
        if no >= len(strings): badnames += 1; continue
        nm = strings[no:].split(b'\0',1)[0].decode('utf-8','replace')
        if not section and nm: imports.append(nm)
        if section and info & 15 == 2: functions.append((value,size,nm))
    cs = capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
    snippet = []
    if name == 'main':
        snippet = [{'address':hex(a),'mnemonic':m,'operands':o} for a,s,m,o in cs.disasm_lite(bytes(image[0x8fd7f0:0x8fd804]),0x8fd7f0)]
    results.append(dict(module=name,sha256=hashlib.sha256(raw).hexdigest(),build_id=raw[0x40:0x48].hex().upper(),
        text_bytes=len(segments[0][1]),dynamic_elf32_syment=tags.get(11),symbol_entries=len(symbols)//16,
        invalid_symbol_name_offsets=badnames,exported_function_symbols=len(functions),
        thumb_tagged_function_symbols=sum(bool(v&1) for v,s,n in functions),imports=len(imports),
        import_examples=imports[:12],sample=snippet))
npdm = (ROOT/'main.npdm').read_bytes()
report = dict(npdm_flags0=hex(npdm[12]),is_64bit_instruction=bool(npdm[12]&1),modules=results,
    limitations=['Symbol counts are not a complete function inventory.', 'Thumb low bits only describe exported symbols.',
                  'A decoded basic-block fragment does not prove executable translation or game compatibility.'])
(OUT/'module-inventory.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
