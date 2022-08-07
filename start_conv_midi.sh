#!/bin/sh
# This script starts MIDI converter mimap5 (github link below)

# Part of hardware MIDI port name - source of messages
HARDWARE_NAME="BlueBoard"

THIS_DIR=$(dirname "$0")
cd "$THIS_DIR" || exit 1

found=$(ps -ef | grep -v grep | grep -c start_conv_midi.sh)
if [ "$found" -gt 2 ]; then
  echo "Exiting, this script is already running"
  exit 1
fi

#wget -nc -O mimap5 https://github.com/slmnv5/mimap5/blob/master/mimap5?raw=true
chmod a+x mimap5

RES=""
PID=1
while true; do
# Start using MIDI source
./mimap5 -r rules.txt -i $HARDWARE_NAME -n PedalCommands "$@" &
PID=$!
sleep 10
RES=$(ps -p $PID -o pid=)
if [ -n "$RES" ]; then exit 0; fi

# Start using typing keyboard
sudo ./mimap5 -r rules.txt -k kbdmap.txt -n PedalCommands "$@" &
PID=$!
sleep 10
RES=$(ps -p $PID -o pid=)
if [ -n "$RES" ]; then stty -echo; exit 0; fi
echo running again

done
