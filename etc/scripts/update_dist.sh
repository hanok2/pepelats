#!/bin/bash

cd ~/pepelats || exit 1
python3 -O -m PyInstaller --add-data="etc:etc" --add-data="start.sh:." \
  --paths="/usr/local/lib/python3.9/dist-packages/" \
  --paths="/usr/lib/python3/dist-packages/" \
  --paths="/usr/lib/python3.9/dist-packages/" \
  --paths="/usr/lib/python3.9/" \
  --add-data="README.md:." --name=pepelatsexe \
  --debug=all --python-option=v \
  --hidden-import="sounddevice" \
  --hidden-import="soundfile"  \
  --hidden-import="mido.backends.rtmidi" \
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
