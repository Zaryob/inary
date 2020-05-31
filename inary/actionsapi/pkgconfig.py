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

# Standart Python Modules
import inary.actionsapi

# INARY Modules
import inary.context as ctx
import subprocess

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class PkgconfigError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[pkgconfig]: " + value)


def getVariableForLibrary(library, variable):
    # Returns a specific variable provided in the library .pc file
    try:
        proc = subprocess.Popen(["pkg-config",
                                 "--variable={}".format(variable),
                                 "{}".format(library)],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        return_code = proc.wait()
    except OSError as exception:
        if exception.errno == 2:
            raise PkgconfigError(
                _("Package pkgconfig is not installed on your system."))
    else:
        if return_code == 0 and proc.stdout:
            return proc.stdout.read().strip()
        else:
            # Command failed
            raise PkgconfigError(proc.stderr.read().strip())


def getLibraryVersion(library):
    """Returns the module version provided in the library .pc file."""
    try:
        proc = subprocess.Popen(["pkg-config",
                                 "--modversion",
                                 library],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        return_code = proc.wait()
    except OSError as exception:
        if exception.errno == 2:
            raise PkgconfigError(
                _("Package pkgconfig is not installed on your system."))
    else:
        if return_code == 0 and proc.stdout:
            return proc.stdout.read().strip()
        else:
            # Command failed
            raise PkgconfigError(proc.stderr.read().strip())


def getLibraryCFLAGS(library):
    """Returns compiler flags for compiling with this library.
    Ex: -I/usr/include/nss"""
    try:
        proc = subprocess.Popen(["pkg-config",
                                 "--cflags",
                                 "{}".format(library)],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        return_code = proc.wait()
    except OSError as exception:
        if exception.errno == 2:
            raise PkgconfigError(
                _("Package pkgconfig is not installed on your system."))
    else:
        if return_code == 0 and proc.stdout:
            return proc.stdout.read().strip()
        else:
            # Command failed
            raise PkgconfigError(proc.stderr.read().strip())


def getLibraryLIBADD(library):
    """Returns linker flags for linking with this library.
    Ex: -lpng14"""
    try:
        proc = subprocess.Popen(["pkg-config",
                                 "--libs",
                                 "{}".format(library)],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        return_code = proc.wait()
    except OSError as exception:
        if exception.errno == 2:
            raise PkgconfigError(
                _("Package pkgconfig is not installed on your system."))
    else:
        if return_code == 0 and proc.stdout:
            return proc.stdout.read().strip()
        else:
            # Command failed
            raise PkgconfigError(proc.stderr.read().strip())


def runManualCommand(*args):
    """Runs the given command and returns the output."""
    cmd = ["pkg-config"]
    cmd.extend(args)
    try:
        proc = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        return_code = proc.wait()
    except OSError as exception:
        if exception.errno == 2:
            raise PkgconfigError(
                _("Package pkgconfig is not installed on your system."))
    else:
        if return_code == 0 and proc.stdout:
            return proc.stdout.read().strip()
        else:
            # Command failed
            raise PkgconfigError(proc.stderr.read().strip())


def libraryExists(library):
    """Returns True if the library provides a .pc file."""
    result = None
    try:
        result = subprocess.call(["pkg-config",
                                  "--exists",
                                  "{}".format(library)])
    except OSError as exception:
        if exception.errno == 2:
            raise PkgconfigError(
                _("Package pkgconfig is not installed on your system."))
    else:
        return result == 0
