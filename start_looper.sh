#!/bin/bash
# This script starts pepelats audio looper
# Optional parameters:
# --use_typing - use typing keys to send MIDI notes
# --debug - show debug messages on screen

# Looper parameters passed via env.
export MAX_LEN_SECONDS=60
export SD_RATE=44100

#check these MIDI ports and use first one found as input
if [ -z "$MIDI_PORT_NAMES" ]; then
  export MIDI_PORT_NAMES='PedalCommands,FakeName1,FakeName2'
fi
#check ALSA devices and use first one found
if [ -z "$USB_AUDIO_NAMES" ]; then
  export USB_AUDIO_NAMES='VALETON GP,USB Audio'
fi

cd_to_script_dir() {
  THIS_DIR=$(dirname "$0")
  cd "$THIS_DIR" || exit 1
}

check_if_running() {
  found=$(ps -ef | grep python3 | grep start_looper.py)
  if [ -n "$found" ]; then
    echo "Exiting, this script is already running"
    exit 1
  fi
}

cd_to_script_dir
check_if_running

CODE_OPTIMIZE="-O"
for var in "$@"; do
  if [ "$var" == "--debug" ]; then
    CODE_OPTIMIZE=""
    break
  fi
done

python_command="python3 $CODE_OPTIMIZE ./start_looper.py  $*"

# keep past 100 lines only
touch ./log.log
tail -n 100 ./log.log >./tmp.log
mv -f ./tmp.log ./log.log

echo "$python_command"

# disable under voltage error on screen as it works OK with under voltage
sudo dmesg -D

# restart many times
for k in {1..100}; do
  echo "started $k time(s)"
  killall -s 9 -w -v python3
  sleep 3
  $python_command
done

sudo dmesg -E
