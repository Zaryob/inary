# -*- coding: utf-8 -*-
#
#
# Copyright (C) 2016 - 2021, Ali Rıza KESKİN (sulincix) and Suleyman POYRAZ (Zaryob)
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
        ctx.ui.error("[GoTools]: " + value)
        if can_access_file('config.log'):
            ctx.ui.error(
                _('Please attach the config.log to your bug report:\n{}/config.log').format(os.getcwd()))


class MakeError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[GoTools]: " + value)


class InstallError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[GoTools]: " + value)


class RunTimeError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[GoTools]: " + value)


def configure(parameters='', installPrefix='', sourceDir='.'):
    """configure source with given Go parameters = "-DGo_BUILD_TYPE -DGo_CXX_FLAGS ... " """
    if not can_access_file(join_path(sourceDir, 'main.go')):
        raise ConfigureError(_('{} not found'.format("main.go")))


def go(parameters=''):
    """use go command from actionsapi"""
    command = 'go {1}'.format(parameters)
    if system(command):
        raise MakeError(_('Make failed.'))


def make(parameters=''):
    """build source with given parameters"""
    command = 'go build {0}'.format(parameters)
    if system(command):
        raise MakeError(_('Make failed.'))


def fixInfoDir():
    infoDir = '{}/usr/share/info/dir'.format(get.installDIR())
    if can_access_file(infoDir):
        unlink(infoDir)


def install(parameters='', argument=''):
    """install source into install directory with given parameters"""
    args = 'GOBIN="{0}/bin" go install \
                 {1} \
                 {2}'.format(get.installDIR(),
                             parameters,
                             argument)

    if system(args):
        raise InstallError(_('Install failed.'))
    else:
        fixInfoDir()


def rawInstall(parameters='', argument=''):
    """rawInstall not available. Using install function"""
    raise RunTimeError(
        _('rawInstall function is not available for gotools. Use install function'))
