#!/bin/bash
# This script starts MIDI converter mimap5 (github link below)

# Part of hardware MIDI port name - source of messages
HARDWARE_NAME="BlueBoard"

THIS_DIR=$(dirname "$0")
cd "$THIS_DIR" || exit 1

found=$(ps -ef | grep -v grep | grep mimap5)
if [ -n "$found" ]; then
  echo "Exiting, mimap5 is already running"
  exit 1
fi

#wget -nc -O mimap5 https://github.com/slmnv5/mimap5/blob/master/mimap5?raw=true
chmod a+x mimap5

hmod a+x mimap5

RES=1
PID=1
while true; do
# Start using MIDI source
./mimap5 -r rules.txt -i $HARDWARE_NAME -n PedalCommands $@ &
PID=$!
sleep 3
RES=$(ps -p $PID -o pid=)
if [ -n "$RES" ]; then exit 0; fi

# Start using typing keyboard
sudo ./mimap5 -r rules.txt -k kbdmap.txt -n PedalCommands $@ &
PID=$!
sleep 3
RES=$(ps -p $PID -o pid=)
if [ -n "$RES" ]; then exit 0; fi
echo running again

done