#!/bin/sh

pwd
PATH=$PATH:.
set -x -e

pisi-cli --ignore-build-no build tests/zip/pspec.xml tests/unzip/pspec.xml
pisi-cli --yes-all --ignore-comar install unzip-5.50-1.pisi zip-2.3-1.pisi

mkdir -p myrepo
cd myrepo
../pisi-cli --ignore-build-no build ../tests/zip2/pspec.xml ../tests/unzip2/pspec.xml
cd ..
pisi-cli --absolute-uris index myrepo
pisi-cli remove-repo repo1
pisi-cli add-repo repo1 pisi-index.xml
pisi-cli list-repo
pisi-cli update-repo repo1
pisi-cli list-available
pisi-cli --install-info list-installed
pisi-cli list-upgrades
pisi-cli --ignore-comar upgrade zip
pisi-cli --install-info list-installed
