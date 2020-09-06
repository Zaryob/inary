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

# Standard Python Modules
import os

# Inary Modules
from inary.util import join_path
import inary.context as ctx

# ActionsAPI Modules
import inary.actionsapi
import inary.actionsapi.get as get
from inary.actionsapi.shelltools import unlink
from inary.actionsapi.shelltools import can_access_file
from inary.actionsapi.shelltools import system


# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class ConfigureError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[CMakeTools]: " + value)
        if can_access_file('config.log'):
            ctx.ui.error(
                _('Please attach the config.log to your bug report:\n{}/config.log').format(os.getcwd()))


class MakeError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[CMakeTools]: " + value)


class InstallError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[CMakeTools]: " + value)


class RunTimeError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[CMakeTools]: " + value)


def configure(parameters='',
              installPrefix='/{}'.format(get.defaultprefixDIR()), sourceDir='.'):
    """configure source with given cmake parameters = "-DCMAKE_BUILD_TYPE -DCMAKE_CXX_FLAGS ... " """
    if can_access_file(join_path(sourceDir, 'CMakeLists.txt')):
        args = 'cmake -DCMAKE_INSTALL_PREFIX={0} \
                      -DCMAKE_INSTALL_LIBDIR={1} \
                      -DCMAKE_C_FLAGS="{7} {2}" \
                      -DCMAKE_CXX_FLAGS="{7} {3}" \
                      -DCMAKE_LD_FLAGS="{4}" \
                      -DCMAKE_BUILD_TYPE=RelWithDebInfo {5} {6}'.format(installPrefix,
                                                                        "/usr/lib32 " if get.buildTYPE() == "emul32" else "/usr/lib",
                                                                        get.CFLAGS(),
                                                                        get.CXXFLAGS(),
                                                                        get.LDFLAGS(),
                                                                        parameters,
                                                                        sourceDir,
                                                                        "-m32" if get.buildTYPE() == "emul32" else "-m64")

        if system(args):
            raise ConfigureError(_('Configure failed.'))
    else:
        raise ConfigureError(
            _('No configure script found. (\"{}\" file not found.)'.format("CMakeLists.txt")))


def make(parameters=''):
    """build source with given parameters"""
    if ctx.config.get_option("verbose") and ctx.config.get_option("debug"):
        command = 'make VERBOSE=1 {0} {1}'.format(get.makeJOBS(), parameters)
    else:
        command = 'make {0} {1} '.format(get.makeJOBS(), parameters)

    if system(command):
        raise MakeError(_('Make failed.'))


def fixInfoDir():
    infoDir = '{}/usr/share/info/dir'.format(get.installDIR())
    if can_access_file(infoDir):
        unlink(infoDir)


def install(parameters='', argument='install'):
    """install source into install directory with given parameters"""
    # You can't squeeze unix paths with things like 'bindir', 'datadir', etc with CMake
    # http://public.kitware.com/pipermail/cmake/2006-August/010748.html
    args = 'make DESTDIR="{0}" \
                 {1} \
                 {2}'.format(get.installDIR(),
                             parameters,
                             argument)

    if system(args):
        raise InstallError(_('Install failed.'))
    else:
        fixInfoDir()


def rawInstall(parameters='', argument='install'):
    """install source into install directory with given parameters = PREFIX=get.installDIR()"""
    if can_access_file('makefile') or can_access_file(
            'Makefile') or can_access_file('GNUmakefile'):
        if system('make {0} {1} '.format(parameters, argument)):
            raise InstallError(_('Install failed.'))
        else:
            fixInfoDir()
    else:
        raise InstallError(_('No Makefile found.'))
