#!/bin/bash
# 马力欧派对 Mac 诊断版（64 GB 别名区 profile_va64），开窗口和声音。日志写到同目录 window_<时间>.log
B=/Volumes/SwitchNative/GameFiles/MarioPartyJamboree/0100965017338000_build
cd "$B/run" && DM_WINDOW=1 DM_AUDIO=1 DM_ROOT="$B" DM_ROMFS="$B/extract/v393216/RomFS" DM_SAVE="$B/run/save" DM_TEMP="$B/run/temp" DM_MSL_DIR="$B/shader/cache" DM_FONT_DIR="$B/font" DM_NVN_SHMAP="$B/profile_va64/0100965017338000/shader_map.tsv" DM_LANG=en-US "$B/tools/dmhost_va64" "$B/patched_v393216" > "/Volumes/SwitchNative/Tools/MarioPartyJamboree/window_$(date +%H%M).log" 2>&1
