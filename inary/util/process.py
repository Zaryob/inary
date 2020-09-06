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
import inary.context as ctx
from os import path, makedirs as mkdirs, environ, access, X_OK

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

try:
    import subprocess
except ImportError:
    raise Exception(_("Module: \'subprocess\' can not imported."))


##############################
# Process Releated Functions #
##############################

def makedirs(dpath):
    if not path.exists(dpath):
        mkdirs(dpath)


def search_executable(executable):
    """Search for the executable in user's paths and return it."""
    for _path in environ["PATH"].split(":"):
        full_path = path.join(_path, executable)
        if path.exists(full_path) and access(full_path, X_OK):
            return full_path
    return None


def run_batch(cmd, ui_debug=True):
    """Run command and report return value and output."""
    ctx.ui.info(_('Running ') + cmd, verbose=True)
    p = subprocess.Popen(cmd, shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if ui_debug:
        ctx.ui.debug(
            _('return value for "{0}" is {1}').format(
                cmd, p.returncode))
    return p.returncode, out.decode('utf-8'), err

# TODO: it might be worthwhile to try to remove the
# use of ctx.stdout, and use run_batch()'s return
# values instead. but this is good enough :)


def run_logged(cmd):
    """Run command and get the return value."""
    ctx.ui.info(_('Running ') + cmd, verbose=True)
    if ctx.stdout:
        stdout = ctx.stdout
    else:
        if ctx.get_option('debug'):
            stdout = None
        else:
            stdout = subprocess.PIPE
    if ctx.stderr:
        stderr = ctx.stderr
    else:
        if ctx.get_option('debug'):
            stderr = None
        else:
            stderr = subprocess.STDOUT

    p = subprocess.Popen(cmd, shell=True, stdout=stdout, stderr=stderr)
    p.communicate()
    ctx.ui.debug(_('return value for "{0}" is {1}').format(cmd, p.returncode))

    return p.returncode


def hewal(expr):
    """Eval with öşex power"""
    expr = str(expr).upper()
    if expr in ("TRUE", "1", "ON", "T", "Y", "YES"):
        return True
    elif expr in ("FALSE", "0", "OFF", "F", "N", "NO"):
        return False
    return None
