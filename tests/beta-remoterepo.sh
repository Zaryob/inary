#!/bin/sh

export PATH=$PATH:.
set -x # xtrace
set -e # errexit

echo "beta functionality test script for testing remote repos"
echo "working directory:" `pwd`
echo "cleaning destination dir: tmp"
rm -rf tmp
#echo "*** repository tests"
pisi-cli add-repo pardus ftp://ftp.uludag.org.tr/pub/pisi/binary/system/base/pisi-index.xml 
pisi-cli update-repo pardus
pisi-cli list-repo

#echo "*** package ops"
pisi-cli list-available
pisi-cli info python
pisi-cli install python

echo "*** database contents"
for x in `find tmp -iname '*.bdb'`; do
    echo "contents of database " $x;
    tools/cat-db.py $x;
done
