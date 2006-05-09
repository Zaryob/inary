#!/bin/sh

argNUM=${#}
if [ ${argNUM} -lt 1 ] ; then
    echo "At least one repo name needed"
    exit 1
fi
./pisi-cli --ignore-comar install `./pisi-cli list-available $@ | tail -n+3 | xargs`
