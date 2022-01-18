#!/bin/bash
# This script starts pepelats audio looper
# There are two version - python file and executable file
# for python version use: $HOME/pepelats/start.sh
# for executable version use: $HOME/pepelatsexe/start.sh

# Two optional parameters:
# --kbd - use typing keyboard keys 1,2,3,4,q,w to send MIDI notes 60,62,64,65,12,13
# --debug - show debug info, works for python version only

#export MAX_LEN_SECONDS=60
#export SD_RATE=48000

cd_to_script_dir() {
  THIS_DIR=$(dirname "$0")
  cd "$THIS_DIR" || exit 1
}

check_if_running() {
  script_name=${BASH_SOURCE[0]}
  for pid in $(pidof -x "$script_name"); do
    if [ "$pid" != "$$" ]; then
      echo "Script $script_name is already running with PID: $pid"
      exit 1
    fi
  done
}

CODE_OPTIMIZE="-O"
for var in "$@"; do
  if [ "$var" == "--debug" ]; then
    CODE_OPTIMIZE=""
    break
  fi
done

USE_KBD=""
for var in "$@"; do
  if [ "$var" == "--kbd" ]; then
    USE_KBD="sudo -E"
    break
  fi
done

python_command="$USE_KBD python3 $CODE_OPTIMIZE ./start.py $*"

cd_to_script_dir
check_if_running

tail -n 100 ./log.log > ./tmp.log
mv -f ./tmp.log ./log.log

#export PYTHONPATH="$THIS_DIR:$THIS_DIR/tests"

# check for linux executable
if [ -f "./pepelatsexe" ]; then
  run_command="$USE_KBD ./pepelatsexe $*"
else
  run_command=$python_command
fi

echo "$run_command"

sudo dmesg -D

# restart many times
for k in {1..100}; do
  echo "started $k time(s)"
  killall -s 9 -w -v python3
  killall -s 9 -w -v pepelatsexe
  sleep 3
  $run_command
done

sudo dmesg -E
