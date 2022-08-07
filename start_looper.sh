#!/bin/sh
# This script starts pepelats audio looper

# Looper parameters passed via env.
export MAX_LEN_SECONDS=60
export SD_RATE=44100

#use this MIDI port as input
export MIDI_PORT_NAME='PedalCommands_out'

#check ALSA devices and use first one found
if [ -z "$USB_AUDIO_NAMES" ]; then
  export USB_AUDIO_NAMES='VALETON GP,USB Audio'
fi

THIS_DIR=$(dirname "$0")
cd "$THIS_DIR" || exit 1

found=$(ps -ef | grep -v grep | grep start_looper.py)
if [ -n "$found" ]; then
  echo "Exiting, already running"
  exit 1
fi

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

# disable under voltage error on screen and disable typing echo
sudo dmesg -D
stty -echo

while true; do
  killall -s 9 -w -v python3
  sleep 10
  $python_command
done

sudo dmesg -E
stty echo

