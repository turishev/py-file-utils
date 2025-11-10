#!/bin/bash
rm -fR pack/dircmp
mkdir -p pack/dircmp/src
cp -Rf etc pack/dircmp
cp -Rf src/dircmp pack/dircmp/src/
rm -Rf pack/dircmp/src/dircmp/__pycache__
cp -f install-dircmp.sh pack/dircmp
cd pack
zip -r dircmp.zip dircmp

