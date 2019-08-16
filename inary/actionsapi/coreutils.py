# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE (Licensed with GPLv2)
# More details about GPLv2, please read the COPYING.OLD file.
#
# Copyright (C) 2016 - 2019, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# Please read the COPYING file.

# Standard Python Modules
import re
import sys


# ActionsAPI


def cat(filename):
    return open(filename)


class grep:
    """keep only lines that match the regexp"""

    def __init__(self, pat, flags=0):
        self.fun = re.compile(pat, flags).match

    def __ror__(self, input):
        return filter(self.fun, input)


class tr:
    """apply arbitrary transform to each sequence element"""

    def __init__(self, transform):
        self.tr = transform

    def __ror__(self, input):
        return map(self.tr, input)


class printto:
    """print sequence elements one per line"""

    def __init__(self, out=sys.stdout):
        self.out = out

    def __ror__(self, input):
        for line in input:
            print(line, file=self.out)


printlines = printto()


class terminator:
    def __init__(self, method):
        self.process = method

    def __ror__(self, input):
        return self.process(input)


aslist = terminator(list)
asdict = terminator(dict)
astuple = terminator(tuple)
join = terminator(''.join)
enum = terminator(enumerate)


class sort:
    def __ror__(self, input):
        ll = list(input)
        ll.sort()
        return ll


sort = sort()


class uniq:
    def __ror__(self, input):
        for i in input:
            try:
                if i == prev:
                    continue
            except NameError:
                pass
            prev = i
            yield i


uniq = uniq()
