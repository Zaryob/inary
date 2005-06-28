#!/bin/sh

pwd
./pisi-build samples/sta*/*.pspec
./pisi-index .
./pisi-updatedb pisi-index.xml
./pisi-install start*pisi
find tmp -iname '*.bdb' | xargs ./cat-db.py
