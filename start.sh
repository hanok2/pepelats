#!/bin/bash
# This script starts pepelats audio looper
# There are two version - python file and executable file
# for python version use: $HOME/pepelats/start.sh
# for executable version use: $HOME/pepelatsexe/start.sh

# Two optional parameters:
# --kbd - use typing keyboard keys 1,2,3,4,q,w to send MIDI notes 60,62,64,65,12,13
# --debug - show debug info, works for python version only

# Looper patrameters passed via env.
#export MAX_LEN_SECONDS=60
#export SD_RATE=48000

# Part of MIDI controller name that you want to connect; To check use: aconnect -l
PEDAL_NAME="BlueBoard"

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
  if [ "$var" == "--kbd" ]; then
    USE_KBD="sudo -E"
    break
  fi
done

EXT_CONV=""
# who will convert MIDI messages - pepelats or binary app. mimap5
if [[ -f mimap5 && -f rules.txt ]]; then
  killall -9 mimap5
  aconnect -x
  ./mimap5 -r rules.txt -n note_counter -vvv &
  time sleep 2
  PEDAL_OUT=$(aconnect -l | awk -v nm="$PEDAL_NAME" '$0 ~ nm {print $2;exit}')
  CLIENT_IN=$(aconnect -l | awk '/note_counter/ {print $2;exit}')
  aconnect -e ${PEDAL_OUT}0 ${CLIENT_IN}0
  if [ $? -eq 0 ]; then
    EXT_CONV="--external_converter"
    echo "========= using external converter for MIDI - mimap5 =============="
  else
    EXT_CONV=""
  fi
fi


python_command="$USE_KBD python3 $CODE_OPTIMIZE ./start.py $EXT_CONV $*"


# keep past 100 lines only
touch ./log.log
tail -n 100 ./log.log > ./tmp.log
mv -f ./tmp.log ./log.log

#export PYTHONPATH="$THIS_DIR:$THIS_DIR/tests"

echo "$python_command"

# disable undervoltage error on screen as it works OK with undervoltage
sudo dmesg -D

# restart many times
for k in {1..100}; do
  echo "started $k time(s)"
  killall -s 9 -w -v python3
  sleep 3
  $python_command
done

sudo dmesg -E
