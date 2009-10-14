
find pisi -iname '*.py' | grep -v pisi/cli/commands.py >exclude
python tools/pygettext.py -D -X exclude -o po/pisi.pot pisi pisi-cli scripts /usr/lib/python2.4/optparse.py
for lang in po/*.po
do
    msgmerge -U $lang po/pisi.pot
done
rm exclude
