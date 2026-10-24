#!/usr/bin/env python3
# main.elf：1) 找线程名字符串被 adrp+add 引用的位置；2) 全段扫描「ldr xA,[xB,#off] … blr xA」型虚调用，off 取解码器虚表偏移，
# 只报告离字符串引用点较近（±0x20000）的，作为影片播放器里的取帧/交帧/还帧调用点。
import struct, sys
sys.path.insert(0, '/Volumes/SwitchNative/Tools/MarioPartyJamboree/rea')
from elfsyms import Elf
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM

e = Elf(sys.argv[1]); img = e.img
names = [b'MoviePlayerThread\0', b'MovieDecoderEventHandler\0', b'MovieVideoInputReadThread\0', b'Bezel:MoviePrepareFrame\0', b'Bezel:MovieLoadBuffer\0']
saddr = {n[:-1].decode(): img.find(n) for n in names}
print('字符串地址', {k: hex(v) for k, v in saddr.items()})
def adrp_target(a, w):
    immlo, immhi = (w >> 29) & 3, (w >> 5) & 0x7ffff
    imm = (immhi << 2) | immlo
    if imm >> 20: imm -= 1 << 21
    return (a & ~0xfff) + (imm << 12)
refs = []
for a in range(0, e.text_end, 4):
    w = struct.unpack_from('<I', img, a)[0]
    if (w & 0x9f000000) != 0x90000000: continue
    rd = w & 31; page = adrp_target(a, w)
    for k in (4, 8, 12):
        w2 = struct.unpack_from('<I', img, a + k)[0]
        if (w2 & 0xffc00000) == 0x91000000 and ((w2 >> 5) & 31) == rd:
            t = page + ((w2 >> 10) & 0xfff)
            for n, s in saddr.items():
                if t == s: refs.append((a, n))
            break
for a, n in refs: print(f'引用 {n} @ main+{a:#x}')
OFF = {0x60: 'AcquireOutputBufferIndex', 0x68: 'GetOutputBuffer', 0x78: 'ReleaseOutputBufferIndex', 0x90: 'GetOutputBufferFormat', 0x88: 'GetOutputBuffer(fmt)', 0x58: 'SendInputBufferForDecode', 0x48: 'AcquireInputBufferIndex'}
md = Cs(CS_ARCH_ARM64, CS_MODE_ARM); md.detail = True
lo = min(a for a, _ in refs) - 0x20000; hi = max(a for a, _ in refs) + 0x20000
win = []
for i in md.disasm(img[lo:hi], lo):
    win.append(i); win = win[-6:]
    if i.mnemonic == 'blr':
        r = i.op_str
        for p in reversed(win[:-1]):
            if p.mnemonic == 'ldr' and p.op_str.startswith(r + ','):
                m = p.op_str.split('#')
                if len(m) == 2:
                    off = int(m[1].rstrip(']'), 16 if '0x' in m[1] else 10)
                    if off in OFF: print(f'main+{i.address:#x}  虚调用 +{off:#x} 可能是 {OFF[off]}   ({p.op_str})')
                break
