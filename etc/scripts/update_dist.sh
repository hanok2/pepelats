#!/bin/bash

# script to make an executable for python application.
# But it looses some dependencies and may crash depending on installed packages

cd ~/pepelats || exit 1
python3 -O -m PyInstaller --add-data="etc:etc" --add-data="start.sh:." \
  --ascii --clean --log-level DEBUG \
  --paths="/usr/local/lib/python3.9/dist-packages/" \
  --paths="/usr/lib/python3/dist-packages/" \
  --paths="/usr/lib/python3.9/dist-packages/" \
  --paths="/usr/lib/python3.9/" \
  --add-data="README.md:." --name=pepelatsexe \
  --debug=all --python-option=v \
  --hidden-import="mido.backends.rtmidi" \
  --collect-binaries "sounddevice" \
  --collect-binaries "soundfile" \
  --noconfirm start.py

exit 0

rsync -av --progress --exclude=".git" --exclude=".gitignore" \
  --exclude="save_song" --delete ./dist/pepelatsexe/ ~/pepelatsexe

# /usr/lib/arm-linux-gnueabihf/libportaudio.so.2

cd ~/pepelatsexe || exit 1
git status
git reset --hard
git add --all
git commit -m"1"
git push
