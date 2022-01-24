#!/bin/bash

cd ~/pepelats || exit 1
python3 -O -m PyInstaller --add-data="etc:etc" --add-data="start.sh:." \
  --add-data="README.md:." --name=pepelatsexe \
  --add-binary="/usr/lib/arm-linux-gnueabihf/libportaudio.so.2:./libportaudio.so" \
  --add-binary="/usr/lib/arm-linux-gnueabihf/libsndfile.so.1:./libsndfile.so" \
  --hidden-import="mido.backends.rtmidi" --noconfirm start.py

rsync -av --progress --exclude=".git" --exclude=".gitignore" \
  --exclude="save_song" --delete ./dist/pepelatsexe/ ~/pepelatsexe

# /usr/lib/arm-linux-gnueabihf/libportaudio.so.2

cd ~/pepelatsexe || exit 1
git status
git reset --hard
git add --all
git commit -m"1"
git push
