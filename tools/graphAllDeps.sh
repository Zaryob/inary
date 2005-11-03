#!/bin/sh

argNUM=${#}
if [ ${argNUM} -lt 1 ] ; then
    echo "At least one repo name needed"
    exit 1
fi

for x in "$@" ; do
    pisi graph `pisi --no-color la ${x} | tail -n+1 | awk -F " - " '{print $1}' | sed -e "s/ //g"`
    fdp -Tpng pgraph.dot -o ~/packageDEP4${x}.png
done
