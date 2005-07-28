#!/bin/sh

pwd
PATH=$PATH:.
set -x
pisi-cli build packages/z/zip/pspec.xml packages/u/unzip/pspec.xml
pisi-cli index .
pisi-cli add-repo repo1 pisi-index.xml
pisi-cli update-repo repo1
# database contents
#find tmp -iname '*.bdb' | xargs tools/cat-db.py
pisi-cli install zip
pisi-cli list-installed
