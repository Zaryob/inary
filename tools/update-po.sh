
find pisi -iname '*.py' | grep -v pisi/cli/commands.py >exclude
python tools/pygettext.py -D -X exclude -o po/pisi.pot pisi pisi-cli scripts /usr/lib/python2.4/optparse.py
msgmerge -U po/tr.po po/pisi.pot
msgmerge -U po/nl.po po/pisi.pot
rm exclude
