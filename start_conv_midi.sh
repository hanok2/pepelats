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

# Start using MIDI source
CMD1="./mimap5 -r rules.txt -i $HARDWARE_NAME -n PedalCommands $@"

# Start using typing keyboard
CMD2="sudo ./mimap5 -r rules.txt -k kbdmap.txt -n PedalCommands $@"

"CMD1" || "CMD2"
while [ $? -ne 0 ]; do
  "CMD1" || "CMD2"
done
