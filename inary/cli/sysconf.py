# -*- coding:utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import optparse

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary.util as util
import inary.cli.command as command
import inary.ui
import inary.data
import inary.errors
import inary.context as ctx
import inary.trigger
import inary.sysconf as sc


class runsysconf(command.PackageOp, metaclass=command.autocommand):
    __doc__ = _("""Run sysconf trigger""")

    def __init__(self, args):
        super(runsysconf, self).__init__(args)

    name = (_("sysconf"), "sc")

    def options(self):
        pass

    def run(self):
        sc.proceed(True)
