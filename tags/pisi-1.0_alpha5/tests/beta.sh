#!/bin/sh

echo "beta functionality test script"
echo "working directory:" `pwd`
echo "cleaning destination dir: tmp"
PATH=$PATH:.
set -x # xtrace
set -e # errexit
rm -rf tmp
#echo "*** build tests"
pisi-cli build https://svn.uludag.org.tr/pisi/trunk/system/base/zip/pspec.xml \
    https://svn.uludag.org.tr/pisi/trunk/system/base/unzip/pspec.xml

#partial-builds
pisi-cli build-setup https://svn.uludag.org.tr/pisi/trunk/system/base/hdparm/pspec.xml
pisi-cli build-build https://svn.uludag.org.tr/pisi/trunk/system/base/hdparm/pspec.xml
pisi-cli build-install https://svn.uludag.org.tr/pisi/trunk/system/base/hdparm/pspec.xml
pisi-cli build-package https://svn.uludag.org.tr/pisi/trunk/system/base/hdparm/pspec.xml

#echo "*** repository tests"

pisi-cli index .
pisi-cli add-repo repo1 pisi-index.xml
pisi-cli update-repo repo1
pisi-cli list-repo

pisi-cli build https://svn.uludag.org.tr/pisi/trunk/system/base/grep/pspec.xml \
    https://svn.uludag.org.tr/pisi/trunk/system/base/flex/pspec.xml

#echo "*** package ops"
pisi-cli info *.pisi
# pisi-cli list-available
pisi-cli install --ignore-comar zip
pisi-cli list-installed
pisi-cli remove  --ignore-comar unzip
pisi-cli install --ignore-comar zip*.pisi
pisi-cli install --ignore-comar hdparm*.pisi flex*.pisi grep*.pisi
pisi-cli remove-repo repo1
# pisi-cli list-available

echo "*** database contents"
for x in `find tmp -iname '*.bdb'`; do
    echo "contents of database " $x;
    tools/cat-db.py $x;
done
