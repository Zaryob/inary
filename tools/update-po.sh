
find inary -iname '*.py' | grep -v inary/cli/commands.py >exclude
pygettext -D -X exclude -o po/inary.pot inary inary-cli scripts
msgmerge -U po/tr.po po/inary.pot
rm exclude
