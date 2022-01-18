#!/bin/bash

cd ~/pepelats || exit 1
python3 -O -m PyInstaller --add-data="etc:etc" --add-data="start.sh:." \
  --add-data="README.md:." --name=pepelatsexe \
  --hidden-import="mido.backends.rtmidi" --noconfirm start.py

rsync -av --progress --exclude=".git" --exclude=".gitignore" \
  --exclude="save_song" --delete ./dist/pepelatsexe/ ~/pepelatsexe

cd ~/pepelatsexe || exit 1
git status
git add --all
git commit -m"1"
git push
