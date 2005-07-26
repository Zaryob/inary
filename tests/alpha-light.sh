#!/bin/sh

pwd
PATH=$PATH:.
pisi-cli build packages/s/star*/pspec.xml
pisi-cli index .
pisi-cli updatedb pisi-index.xml
pisi-cli install start*pisi
echo database contents
find tmp -iname '*.bdb' | xargs ./cat-db.py
