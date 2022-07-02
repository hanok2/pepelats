#!/bin/bash
# This script starts MIDI converter mimap5 (github link below)

# Part of MIDI port name - source of messages
HARDWARE_NAME="BlueBoard"
# MIDI port name that is source of converted messages
EXT_CONV="PedalCommands"

cd_to_script_dir() {
  THIS_DIR=$(dirname "$0")
  cd "$THIS_DIR" || exit 1
}

check_if_running() {
  found=$(ps -ef | grep mimap5)
  if [ -n "$found" ]; then
    echo "Exiting, this script is already running"
    exit 1
  fi
}

cd_to_script_dir
check_if_running

if [[ ! -f rules.txt ]]; then
  wget -O rules.txt https://github.com/slmnv5/mimap5/raw/master/rules.txt
  if [[ ! -f rules.txt ]]; then
    echo "Error downloading rules.txt"
    exit 1
  fi
fi

if [[ ! -f mimap5 ]]; then
  wget -O mimap5 https://github.com/slmnv5/mimap5/blob/master/mimap5?raw=true
  if [[ ! -f mimap5 ]]; then
    echo "Error downloading mimap5"
    exit 1
  fi
  chmod a+x mimap5
fi

HARDWARE_OUT=""
while true; do
  echo "Waiting for MIDI port $HARDWARE_NAME"
  HARDWARE_OUT=$(aconnect -l | awk -v nm="$HARDWARE_NAME" '$0 ~ nm {print $2;exit}')
  if [ -z "$HARDWARE_OUT" ]; then
    sleep 5
  else
    break
  fi
done

# Start converter and create in and out virtual MIDI ports
./mimap5 -r rules.txt -n "$EXT_CONV" &
time sleep 2

CLIENT_IN=$(aconnect -l | awk -v nm="$EXT_CONV" '$0 ~ nm {print $2;exit}')
if aconnect -e "${HARDWARE_OUT}0" "${CLIENT_IN}0"; then
  echo "Connected MIDI $HARDWARE_OUT to  $EXT_CONV"
  exit 0
else
  echo "Failed connect MIDI $HARDWARE_OUT to  $EXT_CONV"
  exit 1
fi
