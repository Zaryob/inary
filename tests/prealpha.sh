#!/bin/sh

pwd
rm -rf tmp
./pisi-build samples/*/*.pspec
./pisi-index .
./pisi-updateindex pisi-index.xml
./pisi-install spec*pisi
./pisi-install popt*pisi
