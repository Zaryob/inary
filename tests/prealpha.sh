#!/bin/sh

pwd
rm -rf tmp
./pisi-build samples/*/*.pspec
./pisi-index .
./pisi-updatedb pisi-index.xml
./pisi-install start*pisi
./pisi-install popt*pisi
find tmp -iname '*.bdb' | xargs ./cat-db.py
