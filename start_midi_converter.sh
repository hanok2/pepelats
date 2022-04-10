#!/bin/bash
# This optional script starts optional MIDI converter mimap5 (link below)
# If this is not used MIDI event conversion is handled by the looper
# If this is used


# Part of hardware MIDI port name that is source of original messages; To check names use: aconnect -l
HARDWARE_NAME="BlueBoard"
# Full MIDI port name that is source of converted messages
CONVERTED_NAME="external_converter"

THIS_DIR=$(dirname "$0")
cd "$THIS_DIR" || exit 1

if [[ ! -f rules.txt ]]; then
  wget -O rules.txt https://github.com/slmnv5/mimap5/raw/master/rules.txt
  if [[ ! -f rules.txt ]]; then
    echo "!!!!!!!! Error downloading rules.txt !!!!!!!!!!!!!"
    exit 1
  fi
fi

if [[ ! -f mimap5 ]]; then
  wget -O mimap5 https://github.com/slmnv5/mimap5/blob/master/mimap5?raw=true
  if [[ ! -f mimap5 ]]; then
    echo "!!!!!!!! Error downloading mimap5 !!!!!!!!!!!!!"
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

if [ -z "$HARDWARE_OUT" ]; then
    echo "!!!!!!!! Error opening port $HARDWARE_NAME !!!!!!!!!!!!!"
    exit 1
fi


# Kill and disconnect all
killall -9 mimap5
aconnect -x
# Start client and create MIDI port $CONVERTED_NAME
# This port must be #1 in the MIDI port names list for the looper

./mimap5 -r rules.txt -n "$CONVERTED_NAME" &
time sleep 2

CLIENT_IN=$(aconnect -l | awk -v nm="$CONVERTED_NAME" '$0 ~ nm {print $2;exit}')
if aconnect -e "${HARDWARE_OUT}0" "${CLIENT_IN}0"; then
  echo "========= Connected to MIDI port $CONVERTED_NAME =============="
  exit 0
else
  echo "!!!!!!!! Failed connect to MIDI port $CONVERTED_NAME !!!!!!!!!!!!!"
  exit 1
fi



