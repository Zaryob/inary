#!/bin/sh

pwd
PATH=$PATH:.
set -x
pisi-cli build https://svn.uludag.org.tr/pisi/trunk/z/zip/pspec.xml https://svn.uludag.org.tr/pisi/trunk/u/unzip/pspec.xml
pisi-cli index .
pisi-cli add-repo repo1 pisi-index.xml
pisi-cli update-repo repo1
# database contents
#find tmp -iname '*.bdb' | xargs tools/cat-db.py
pisi-cli install zip
pisi-cli list-installed
pisi-cli remove unzip
pisi-cli install zip*.pisi
