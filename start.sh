#!/bin/bash
# This script starts pepelats audio looper
# Optional parameters:
# --use_typing - use typing keys defined in ./etc/count/kbd_notes.json

# Looper parameters passed via env.
export MAX_LEN_SECONDS=60
export SD_RATE=44100

cd_to_script_dir() {
  THIS_DIR=$(dirname "$0")
  cd "$THIS_DIR" || exit 1
}

check_if_running() {
  script_name=${BASH_SOURCE[0]}
  for pid in $(pidof -x "$script_name"); do
    if [ "$pid" != "$$" ]; then
      echo "Exiting. Script $script_name is already running with PID: $pid"
      exit 1
    fi
  done
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

USE_KBD=""
for var in "$@"; do
  if [ "$var" == "--use_typing" ]; then
    USE_KBD="sudo -E"
    break
  fi
done

python_command="$USE_KBD python3 $CODE_OPTIMIZE ./start.py  $*"

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
