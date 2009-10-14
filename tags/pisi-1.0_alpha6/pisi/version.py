# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# version structure

# Authors:  Eray Ozkural <eray@uludag.org.tr>

import re

import pisi.util as util


# Basic rule is:
# p > (no suffix) > rc > pre > beta > alpha
keywords = {"alpha": 0,
            "beta" : 1,
            "pre"  : 2,
            "rc"   : 3,
            "NOKEY" : 4,
            "p"    : 5}

# helper functions
def has_keyword(versionitem):
    if versionitem._keyword != "NOKEY":
        return True

    return False


class VersionItem:
    _keyword = "NOKEY"
    _value = 0

    def __init__(self, itemstring):

        for keyword in keywords.keys():
            if itemstring.startswith(keyword):

                if self._keyword == "NOKEY":
                    self._keyword = keyword
                else:
                    # longer match is correct
                    if len(keyword) > len(self._keyword):
                        self._keyword = keyword
        
        if self._keyword == "NOKEY":
            self._value = itemstring
        else:
            # rest is the version item's value. And each must have
            # one!
            self._value = itemstring[len(self._keyword):]

    def __lt__(self,rhs):
        l = keywords[self._keyword]
        r = keywords[rhs._keyword]
        if l < r:
            return True
        elif l == r: 
            return self._value < rhs._value
        else: # l > r
            return False

    def __le__(self,rhs):
        l = keywords[self._keyword]
        r = keywords[rhs._keyword]
        if l < r:
            return True
        elif l == r:
            return self._value <= rhs._value
        else: # l > r
            return False

    def __gt__(self,rhs):
        l = keywords[self._keyword]
        r = keywords[rhs._keyword]
        if l > r:
            return True
        elif l == r:
            return self._value > rhs._value
        else: # l < r
            return False

    def __ge__(self,rhs):
        l = keywords[self._keyword]
        r = keywords[rhs._keyword]
        if l > r:
            return True
        elif l == r:
            return self._value >= rhs._value
        else: # l < r
            return False
                


class Version:

    def __init__(self, verstring):
        self.comps = []
        for i in util.multisplit(verstring,'.-_'):
            # some version strings can contain ascii chars at the
            # back. As an example: 2.11a
            # We split '11a' as two items like '11' and 'a'
            s = re.compile("[a-z-A-Z]$").search(i)
            if s:
                head = i[:s.start()]
                tail = s.group()
                self.comps.append(VersionItem(head))
                self.comps.append(VersionItem(tail))
            else:
                self.comps.append(VersionItem(i))

        self.verstring = verstring

    def string(self):
        return self.verstring

    def pred(self, rhs, pred):
        
        loop = len(self.comps)
        if len(rhs.comps) > loop:
            loop = len(rhs.comps)

        for i in range(0, loop):
            try:
                litem = self.comps[i]
            except IndexError:
                litem = VersionItem("")

            try:
                ritem = rhs.comps[i]
            except IndexError:
                ritem = VersionItem("")

            if pred(litem, ritem):
                return True

        else:
            return False

    def __lt__(self,rhs):
        return self.pred(rhs, lambda x,y: x<y)

    def __le__(self,rhs):
        return self.pred(rhs, lambda x,y: x<=y)

    def __gt__(self,rhs):
        return self.pred(rhs, lambda x,y: x>y)

    def __ge__(self,rhs):
        return self.pred(rhs, lambda x,y: x>=y)
