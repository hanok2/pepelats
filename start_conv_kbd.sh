#!/bin/bash
# This script starts MIDI converter mimap5 (github link below) using typing keyboard


THIS_DIR=$(dirname "$0")
cd "$THIS_DIR" || exit 1

found=$(ps -ef | grep mimap5)
if [ -n "$found" ]; then
  echo "Exiting, mimap5 is already running"
  exit 1
fi

#wget -nc -O mimap5 https://github.com/slmnv5/mimap5/blob/master/mimap5?raw=true
chmod a+x mimap5

# Start converter and create in and out virtual MIDI ports using typing keyboard only
sudo ./mimap5 -r rules.txt -k kbdmap.txt "$@" &


