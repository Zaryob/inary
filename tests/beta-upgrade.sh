#!/bin/sh

pwd
PATH=$PATH:.
set -x -e

pisi-cli build tests/zip/pspec.xml tests/unzip/pspec.xml
pisi-cli --yes-all --ignore-comar install unzip-5.50-1.pisi zip-2.3-1.pisi

mkdir -p myrepo
cd myrepo
../pisi-cli build ../tests/zip2/pspec.xml ../tests/unzip2/pspec.xml
cd ..
pisi-cli index myrepo
pisi-cli remove-repo myrepo
pisi-cli add-repo myrepo pisi-index.xml
pisi-cli list-repo
pisi-cli update-repo myrepo
pisi-cli list-available
pisi-cli --ignore-comar upgrade zip
pisi-cli list-installed
