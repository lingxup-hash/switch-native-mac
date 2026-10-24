#!/bin/bash
set -euo pipefail
source '/Volumes/SwitchNative/Tools/Splatoon3/env.sh'
input_dir="${1:-/Volumes/SwitchNative/GameFiles/Splatoon3}"
if [[ ! -d "$input_dir" ]]; then
  echo 'Game folder does not exist.' >&2
  exit 2
fi
cd '/Volumes/SwitchNative/Projects/nxnative-splatoon3'
exec python scripts/build_ipa_from_nsp.py "$input_dir" -k '/Volumes/T7 Shield/prod.keys' --platform mac --survey-only --progress lines
