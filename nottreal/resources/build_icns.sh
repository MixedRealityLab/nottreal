#!/bin/bash

# from https://stackoverflow.com/a/20703594

rm -rf appicon.iconset
mkdir appicon.iconset
sips -z 16 16     appicon-32.png     --out appicon.iconset/icon_16x16.png
sips -z 32 32     appicon-32.png     --out appicon.iconset/icon_16x16@2x.png
sips -z 32 32     appicon-32.png     --out appicon.iconset/icon_32x32.png
sips -z 64 64     appicon-32@2x.png  --out appicon.iconset/icon_32x32@2x.png
sips -z 128 128   appicon-128.png    --out appicon.iconset/icon_128x128.png
sips -z 256 256   appicon-128@2x.png --out appicon.iconset/icon_128x128@2x.png
sips -z 256 256   appicon-256.png    --out appicon.iconset/icon_256x256.png
sips -z 512 512   appicon-256@2x.png --out appicon.iconset/icon_256x256@2x.png
sips -z 512 512   appicon-512.png --out appicon.iconset/icon_512x512.png
cp appicon-512@2x.png appicon.iconset/icon_512x512@2x.png
iconutil -c icns appicon.iconset
rm -R appicon.iconset

rm -rf file.iconset
mkdir file.iconset
sips -z 16 16     file-32.png     --out file.iconset/icon_16x16.png
sips -z 32 32     file-32.png     --out file.iconset/icon_16x16@2x.png
sips -z 32 32     file-32.png     --out file.iconset/icon_32x32.png
sips -z 64 64     file-32@2x.png  --out file.iconset/icon_32x32@2x.png
sips -z 128 128   file-128.png    --out file.iconset/icon_128x128.png
sips -z 256 256   file-128@2x.png --out file.iconset/icon_128x128@2x.png
sips -z 256 256   file-256.png    --out file.iconset/icon_256x256.png
sips -z 512 512   file-256@2x.png --out file.iconset/icon_256x256@2x.png
sips -z 512 512   file-512.png --out file.iconset/icon_512x512.png
cp file-512@2x.png file.iconset/icon_512x512@2x.png
iconutil -c icns file.iconset
rm -R file.iconset