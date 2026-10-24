# Load with: source /Volumes/SwitchNative/Tools/switch-env.sh
if [ ! -d /Volumes/SwitchNative/Cache/Homebrew ]; then
  echo "SwitchNative is not mounted. Mount the T7 disk image first." >&2
  return 1
fi
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:$PATH"
export HOMEBREW_CACHE="/Volumes/SwitchNative/Cache/Homebrew"
export HOMEBREW_TEMP="/Volumes/SwitchNative/Temp"
export TMPDIR="/Volumes/SwitchNative/Temp/"
