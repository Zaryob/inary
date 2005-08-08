#!/bin/sh

pwd
PATH=$PATH:.
set -x -e
pisi-cli build tests/zip/pspec.xml tests/unzip/pspec.xml
pisi-cli index .
pisi-cli add-repo repo1 pisi-index.xml
pisi-cli update-repo repo1
pisi-cli --ignore-comar install zip
pisi-cli list-installed
pisi-cli --ignore-comar remove unzip
pisi-cli --ignore-comar install zip*.pisi
