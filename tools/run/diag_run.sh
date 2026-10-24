#!/bin/bash
# 马力欧派对诊断运行：64 GB 别名区 host、存档副本（diag/save，不碰 run/save）、DM_CTL 自动按键与截图。
# 用法: diag_run.sh <秒数> <标签> [额外环境变量...]   例: diag_run.sh 120 plaza DM_NVN_PASSDUMP=3000
# 截图在 diag/shots_<标签>/，日志在 Tools/MarioPartyJamboree/diag_<标签>_<时间>.log
B=/Volumes/SwitchNative/GameFiles/MarioPartyJamboree/0100965017338000_build
T=/Volumes/SwitchNative/Tools/MarioPartyJamboree
SECS=${1:-120}; TAG=${2:-run}; shift 2
SHOTS=$B/diag/shots_$TAG; mkdir -p "$SHOTS"
CTL=$B/diag/ctl_$TAG.txt; : > "$CTL"
LOG=$T/diag_${TAG}_$(date +%H%M).log; echo "$LOG"
# 控制线程：每 3 秒按一次 A（跳过片头/对话），每 10 秒截一张图
( for ((s=3; s<SECS; s+=3)); do sleep 3; echo "A" >> "$CTL"; if (( s % 9 == 0 )); then echo "shot $SHOTS/t$(printf %03d $s).png" >> "$CTL"; fi; done ) &
CP=$!
cd "$B/run" && env DM_CTL="$CTL" DM_ROOT="$B" DM_ROMFS="$B/extract/v393216/RomFS" DM_SAVE="$B/diag/save" DM_TEMP="$B/diag/temp" \
  DM_MSL_DIR="$B/shader/cache" DM_FONT_DIR="$B/font" DM_NVN_SHMAP="$B/profile_va64/0100965017338000/shader_map.tsv" DM_LANG=en-US "$@" \
  perl -e "alarm $SECS; exec @ARGV" "$B/tools/dmhost_diag" "$B/patched_v393216" > "$LOG" 2>&1
kill $CP 2>/dev/null
ls "$SHOTS" | tail -3
