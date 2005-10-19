#!/bin/sh

pwd
PATH=$PATH:.
set -x
pisi-cli -Dtmp clean
pisi-cli -B -Dtmp remove unzip
set -e
pisi-cli -Dtmp -E --ignore-build-no build tests/zip/pspec.xml tests/unzip/pspec.xml
pisi-cli -Dtmp index .
#pisi-cli -Dtmp remove-repo repo1
pisi-cli -Dtmp add-repo repo1 pisi-index.xml
pisi-cli -Dtmp list-repo
pisi-cli -Dtmp update-repo repo1
pisi-cli -Dtmp list-available
pisi-cli -Dtmp --ignore-comarinstall zip
pisi-cli -Dtmp list-installed
pisi-cli -Dtmp --ignore-comar remove unzip
pisi-cli -Dtmp info zip*.pisi
pisi-cli -Dtmp --ignore-comar install zip*.pisi
pisi-cli -Dtmp list-pending
pisi-cli -Dtmp configure-pending
