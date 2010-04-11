#!/bin/sh

PYTHON_VER=`python -c "import sys; print '%d.%d' % sys.version_info[:2]"`

find pisi -iname '*.py' | grep -v pisi/cli/commands.py > exclude
python scripts/pygettext.py -D -X exclude -o po/pisi.pot pisi pisi-cli /usr/lib/python$PYTHON_VER/optparse.py
for lang in po/*.po
do
    msgmerge -U $lang po/pisi.pot
done
rm exclude
