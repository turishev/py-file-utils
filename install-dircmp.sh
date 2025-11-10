#!/bin/bash
DST_DIR=${HOME}/.local/share
mkdir -p ${DST_DIR}/icons
cp -f ./etc/dircmp.png  ${DST_DIR}/icons
cp -f ./etc/dircmp.desktop ${DST_DIR}/applications
cp -fR ./src/dircmp  ${DST_DIR}

