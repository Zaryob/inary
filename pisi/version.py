# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 - 2010, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

"""version structure"""

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi

# Basic rule is:
# p > (no suffix) > m > rc > pre > beta > alpha
# m: milestone. this was added for OO.o
# p: patch-level
__keywords = (
        ("alpha",   -5),
        ("beta",    -4),
        ("pre",     -3),
        ("rc",      -2),
        ("m",       -1),
        ("p",        1),
        )

class InvalidVersionError(pisi.Error):
    pass

def __make_version_item(v):
    try:
        return int(v), None
    except ValueError:
        return int(v[:-1]), v[-1]

def make_version(version):
    ver, sep, suffix = version.partition("_")
    try:
        if sep:
            # "s" is a string greater than the greatest keyword "rc"
            if "a" <= suffix <= "s":
                for keyword, value in __keywords:
                    if suffix.startswith(keyword):
                        return map(__make_version_item, ver.split(".")), value, \
                                map(__make_version_item, suffix[len(keyword):].split("."))
                else:
                    # Probably an invalid version string. Reset ver string
                    # to raise an exception in __make_version_item function.
                    ver = ""
            else:
                return map(__make_version_item, ver.split(".")), 0, \
                        map(__make_version_item, suffix.split("."))

        return map(__make_version_item, ver.split(".")), 0, [(0, None)]

    except ValueError:
        raise InvalidVersionError(_("Invalid version string: '%s'") % version)

class Version(object):

    __slots__ = ("__version", "__version_string")

    @staticmethod
    def valid(version):
        try:
            make_version(version)
        except InvalidVersionError:
            return False
        return True

    def __init__(self, verstring):
        self.__version_string = verstring
        self.__version = make_version(verstring)

    def string(self):
        return self.__version_string

    def compare(self, ver):
        if isinstance(ver, basestring):
            return cmp(self.__version, make_version(ver))

        return cmp(self.__version, ver.__version)

    def __lt__(self, rhs):
        if isinstance(rhs, basestring):
            return self.__version < make_version(rhs)

        return self.__version < rhs.__version

    def __le__(self, rhs):
        if isinstance(rhs, basestring):
            return self.__version <= make_version(rhs)

        return self.__version <= rhs.__version

    def __gt__(self, rhs):
        if isinstance(rhs, basestring):
            return self.__version > make_version(rhs)

        return self.__version > rhs.__version

    def __ge__(self, rhs):
        if isinstance(rhs, basestring):
            return self.__version >= make_version(rhs)

        return self.__version >= rhs.__version

    def __eq__(self, rhs):
        if isinstance(rhs, basestring):
            return self.__version_string == rhs

        return self.__version_string == rhs.__version_string

    def __str__(self):
        return self.__version_string
