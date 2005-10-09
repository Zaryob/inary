#! /bin/sh

find . -iname '*.py' | xargs pygettext -D -opo/pisi.pot

