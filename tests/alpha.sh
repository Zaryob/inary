#!/bin/sh

echo "alpha functionality test script"
echo "working directory:" `pwd`
#rm -rf tmp
echo "*** build tests"
pisi-cli build https://svn.uludag.org.tr/pisi/trunk/z/zip/pspec.xml \
 https://svn.uludag.org.tr/pisi/trunk/u/unzip/pspec.xml
echo "*** repository tests"

echo "*** package ops"

for x in tmp -iname '*.bdb'; do
    echo "contents of database " $x;
    cat-db.py;
done
