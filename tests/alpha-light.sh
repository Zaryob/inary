#!/bin/sh

pwd
PATH=$PATH:.
set -x
pisi-cli build packages/z/zip/pspec.xml packages/u/unzip/pspec.xml
pisi-cli index .
pisi-cli updatedb pisi-index.xml
# database contents
find tmp -iname '*.bdb' | xargs tools/cat-db.py
pisi-cli install zip
