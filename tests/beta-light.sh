#!/bin/sh

pwd
PATH=$PATH:.
set -x
pisi-cli --ignore-comar remove unzip
set -e
pisi-cli --ignore-build-no build tests/zip/pspec.xml tests/unzip/pspec.xml
pisi-cli index .
pisi-cli add-repo repo1 pisi-index.xml
pisi-cli list-repo
pisi-cli update-repo repo1
pisi-cli list-available
pisi-cli --ignore-comar install zip
pisi-cli list-installed
pisi-cli --ignore-comar remove unzip
pisi-cli info zip*.pisi
pisi-cli --ignore-comar install zip*.pisi
pisi-cli list-pending
pisi-cli configure-pending
