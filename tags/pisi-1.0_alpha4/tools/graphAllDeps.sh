#!/bin/sh

argNUM=${#}
if [ ${argNUM} -lt 1 ] ; then
    echo "At least one repo name needed"
    exit 1
fi

for x in "$@" ; do
    ./pisi-cli graph `./pisi-cli list-available $x | tail -n+3 | xargs`
    dot -Tpng pgraph.dot -o ~/packageDEP4${x}.png
done
