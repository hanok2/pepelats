# Pepelats - Software looper on Raspberry Pi.

## Features

- Arbitrary number of song parts (verse/chorus/bridge) each made of any number of parallel loops
- Parallel loops in song part may have different length (number of bars)
- Song parts and loops have "undo/redo" and may be added/deleted on the run
- Automatic drums with changing patterns, fills and endings. Patterns are editable in a text file
- Timing of changing parts and recording is adjusted to keep rhythm intact - quantization feature
- Songs may be saved and loaded from SD card
- MIDI over Bluetooth or USB is easy to configure in a text file. Users may adjust buttons to their needs.
- Text console shows loop position, state, length and volume of each part and loop
- Menu to display and change looper parameters using only foot controller
- Simple installation with executable file in repository


## Installation:

Install Raspberry Pi OS Lite, LCD screen and drivers.

Install dependencies running script [install_dependencies.sh](etc/scripts/install_dependencies.sh)

Clone this repository: 
- cd ~/; git clone https://github.com/slmnv5/pepelats

To make text readable on 3.5 inch LCD select font Terminus 16x32 using command:

- sudo dpkg-reconfigure console-setup

To enable auto start edit ~/.bashrc file, append this line:

- $HOME/pepelats/start.sh


# [Pepelats details](./Details.md)
