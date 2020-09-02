# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2020, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

"""misc. utility functions, including process and file utils"""

from inary.util.strings import *
import struct
from functools import reduce
import os

# Inary Modules
import inary
import inary.errors
import inary.context as ctx

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


#############################
# Path Processing Functions #
#############################


def splitpath(a):
    """split path into components and return as a list
    os.path.split doesn't do what I want like removing trailing /"""
    comps = a.split(os.path.sep)
    if comps[len(comps) - 1] == '':
        comps.pop()
    return comps


def makepath(comps, relative=False, sep=os.path.sep):
    """Reconstruct a path from components."""
    path = reduce(lambda x, y: x + sep + y, comps, '')
    if relative:
        return path[len(sep):]
    else:
        return path


def parentpath(a, sep=os.path.sep):
    # remove trailing '/'
    a = a.rstrip(sep)
    return a[:a.rfind(sep)]


def parenturi(a):
    return parentpath(a, '/')


def subpath(a, b):
    """Find if path a is before b in the directory tree."""
    return prefix(splitpath(a), splitpath(b))


def removepathprefix(prefix, path):
    """Remove path prefix a from b, finding the pathname rooted at a."""
    comps = remove_prefix(splitpath(prefix), splitpath(path))
    if len(comps) > 0:
        return join_path(*tuple(comps))
    else:
        return ""


def join_path(a, *p):
    """Join two or more pathname components.
    Python os.path.join cannot handle '/' at the start of latter components.
    """
    path = a
    for b in p:
        b = b.lstrip('/')
        if path == '' or path.endswith('/'):
            path += b
        else:
            path += '/' + b
    return path
