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

# Inary Modules
import inary.context as ctx

# ActionsAPI Modules
import inary.actionsapi
import inary.actionsapi.get as get
from inary.actionsapi.shelltools import system

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class MakeError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[Scons]: " + value)


class InstallError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[Scons]: " + value)


def make(parameters=''):
    if system('scons {0} {1}'.format(get.makeJOBS(), parameters)):
        raise MakeError(_('Make failed.'))


def install(parameters='install', prefix=get.installDIR(), argument='prefix'):
    if system('scons {0}={1} {2}'.format(argument, prefix, parameters)):
        raise InstallError(_('Install failed.'))
