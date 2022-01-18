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

## Two repositories:

Code repo (needs installation of Python and dependencies):

- https://github.com/slmnv5/pepelats

Executable repo:

- https://github.com/slmnv5/pepelatsexe

## Installation:

Install Raspberry Pi OS Lite, LCD screen and drivers, I added few notes below, it may be helpful. There is executable
repository for this looper and installation needs only one git clone command:

- cd ~/; git clone https://github.com/slmnv5/pepelatsexe

To enable auto start edit ~/.bashrc file, append this line:

- $HOME/pepelatsexe/start.sh

# [Pepelats details](./Details.md)
