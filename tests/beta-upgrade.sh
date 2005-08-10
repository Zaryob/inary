#!/bin/sh

pwd
PATH=$PATH:.
set -x -e

pisi-cli build tests/zip/pspec.xml tests/unzip/pspec.xml
pisi-cli --ignore-comar install zip*.pisi unzip*.pisi
rm -f *.pisi

pisi-cli build tests/zip2/pspec.xml tests/unzip2/pspec.xml
pisi-cli index .
pisi-cli add-repo repo1 pisi-index.xml
pisi-cli list-repo
pisi-cli update-repo repo1
pisi-cli list-available
pisi-cli --ignore-comar upgrade zip
pisi-cli list-installed
