find pisi -iname '*.py' | grep -v pisi/cli/commands.py >exclude
pygettext.py -D -X exclude -o po/pisi.pot pisi
msgmerge -U po/tr.po po/pisi.pot
rm exclude
