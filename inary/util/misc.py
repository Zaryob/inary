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

import os

# Inary Modules
from unicodedata import category as ucategory
import inary.context as ctx
from os import listdir, path, readlink, rmdir
from sys import maxunicode
from inary.util.files import sha1_file, sha1_data

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


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


def colorize(msg, color):
    """Colorize the given message for console output"""
    if color in ctx.const.colors and not (ctx.get_option(
            'no_color') or ctx.config.values.general.no_color):
        return str(ctx.const.colors[color] + msg + ctx.const.colors['default'])
    else:
        return str(msg)


def config_changed(config_file):
    fpath = join_path(ctx.config.dest_dir(), config_file.path)
    if path.exists(fpath) and not path.isdir(fpath):
        if path.islink(fpath):
            f = readlink(fpath)
            if os.path.exists(f) and sha1_data(f) != config_file.hash:
                return True
        else:
            if sha1_file(fpath) != config_file.hash:
                return True
    return False


# recursively remove empty dirs starting from dirpath
def rmdirs(dirpath):
    if path.isdir(dirpath) and not listdir(dirpath):
        ctx.ui.info(
            _("Removing empty dir: \"{}\"").format(dirpath),
            verbose=True)
        rmdir(dirpath)
        rmdirs(path.dirname(dirpath))


# Python regex sucks
# http://mail.python.org/pipermail/python-list/2009-January/523704.html
def letters():
    start = end = None
    result = []
    for index in range(maxunicode + 1):
        c = chr(index)
        if ucategory(c)[0] == 'L':
            if start is None:
                start = end = c
            else:
                end = c
        elif start:
            if start == end:
                result.append(start)
            else:
                result.append(start + "-" + end)
            start = None
    return ''.join(result)
