#!/bin/sh

set -x # xtrace
set -e # errexit

echo "beta functionality test script"
echo "working directory:" `pwd`
echo "cleaning destination dir: tmp"
rm -rf tmp
#echo "*** build tests"
pisi-cli build https://svn.uludag.org.tr/pisi/trunk/system/base/zip/pspec.xml \
    https://svn.uludag.org.tr/pisi/trunk/system/base/unzip/pspec.xml

#partial-builds
pisi-cli build-dosetup https://svn.uludag.org.tr/pisi/trunk/system/base/hdparm/pspec.xml
pisi-cli build-dobuild https://svn.uludag.org.tr/pisi/trunk/system/base/hdparm/pspec.xml
pisi-cli build-doinstall https://svn.uludag.org.tr/pisi/trunk/system/base/hdparm/pspec.xml
pisi-cli build-dopackage https://svn.uludag.org.tr/pisi/trunk/system/base/hdparm/pspec.xml

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
pisi-cli install zip
pisi-cli list-installed
pisi-cli remove unzip
pisi-cli install zip*.pisi
pisi-cli install hdparm*.pisi flex*.pisi grep*.pisi
pisi-cli remove-repo repo1
# pisi-cli list-available

echo "*** database contents"
for x in `find tmp -iname '*.bdb'`; do
    echo "contents of database " $x;
    tools/cat-db.py $x;
done
