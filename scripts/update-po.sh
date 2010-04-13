#!/bin/sh

PYTHON_VER=`python -c "import sys; print '%d.%d' % sys.version_info[:2]"`
OPTPARSE_PY=/usr/lib/python$PYTHON_VER/optparse.py

find pisi -iname '*.py' | grep -v pisi/cli/commands.py > exclude
echo "$OPTPARSE_PY" >> exclude
python scripts/pygettext.py -D -X exclude -o po/pisi.pot pisi pisi-cli $OPTPARSE_PY
for lang in po/*.po
do
    msgmerge --update --no-wrap --sort-by-file $lang po/pisi.pot
done
rm exclude
