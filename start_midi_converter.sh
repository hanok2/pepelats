#!/bin/bash
# This script starts optional MIDI converter (found at https://github.com/slmnv5/mimap5.git)
# Part of MIDI port name that is source of RAW messages; To check use: aconnect -l
RAW_NAME="BlueBoard"
# Full MIDI port name that is source of CONVERTED messages
CONVERTED_NAME="note_counter"

cd_to_script_dir() {
  THIS_DIR=$(dirname "$0")
  cd "$THIS_DIR" || exit 1
}

cd_to_script_dir

if [[ -f rules.txt ]]; then
  wget https://raw.githubusercontent.com/slmnv5/mimap5/rules.txt
fi

if [[ -f mimap5 ]]; then
  wget https://raw.githubusercontent.com/slmnv5/mimap5/mimap5
fi

# Start mimap5 and create MIDI port $CONVERTED_NAME
# This port must be #1 in the MIDI port names list for the looper

killall -9 mimap5
aconnect -x
./mimap5 -r rules.txt -n note_counter &
time sleep 2
PEDAL_OUT=$(aconnect -l | awk -v nm="$RAW_NAME"        '$0 ~ nm {print $2;exit}')
CLIENT_IN=$(aconnect -l | awk -v nm="$CONVERTED_NAME"  '$0 ~ nm {print $2;exit}')
if aconnect -e "${PEDAL_OUT}0" "${CLIENT_IN}0"; then
  echo "========= started MIDI converter mimap5, MIDI port name $CONVERTED_NAME =============="
  exit 0
else
  echo "!!!!!!!! Error starting MIDI converter mimap5 !!!!!!!!!!!!!"
  exit 1
fi



