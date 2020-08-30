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

# Inary Modules
import inary
import inary.errors
import inary.context as ctx

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import unicodedata
import sys

def colorize(msg, color):
    """Colorize the given message for console output"""
    if color in ctx.const.colors and not (ctx.get_option(
            'no_color') or ctx.config.values.general.no_color):
        return str(ctx.const.colors[color] + msg + ctx.const.colors['default'])
    else:
        return str(msg)


def config_changed(config_file):
    fpath = join_path(ctx.config.dest_dir(), config_file.path)
    if os.path.exists(fpath) and not os.path.isdir(fpath):
        if os.path.islink(fpath):
            f = os.readlink(fpath)
            if os.path.exists(f) and sha1_data(f) != config_file.hash:
                return True
        else:
            if sha1_file(fpath) != config_file.hash:
                return True
    return False


# recursively remove empty dirs starting from dirpath
def rmdirs(dirpath):
    if os.path.isdir(dirpath) and not os.listdir(dirpath):
        ctx.ui.info(
            _("Removing empty dir: \"{}\"").format(dirpath),
            verbose=True)
        os.rmdir(dirpath)
        rmdirs(os.path.dirname(dirpath))


# Python regex sucks
# http://mail.python.org/pipermail/python-list/2009-January/523704.html
def letters():
    start = end = None
    result = []
    for index in range(sys.maxunicode + 1):
        c = chr(index)
        if unicodedata.category(c)[0] == 'L':
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

