#!/bin/sh
# Create a folder (named dmg) to prepare our DMG in (if it doesn't already exist).
mkdir -p dist/dmg
# Empty the dmg folder.
rm -r dist/dmg/*
# Copy the app bundle to the dmg folder.
cp -r "dist/D&S ParGenerator.app" dist/dmg
# If the DMG already exists, delete it.
test -f "dist/D&S ParGenerator.dmg" && rm "dist/D&S ParGenerator.dmg"
create-dmg \
    --volname "D&S ParGenerator" \
    --volicon "icons/LukeWare_icon.icns" \
    --window-pos 200 120 \
    --window-size 600 300 \
    --icon-size 100 \
    --icon "D&S ParGenerator.app" 175 120 \
    --hide-extension "D&S ParGenerator.app" \
    --app-drop-link 425 120 \
    "dist/D&S ParGenerator.dmg" \
    "dist/dmg/"
