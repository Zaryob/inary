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

import inary.trigger
import inary.context as ctx
import inary.errors
import inary.data
import inary.ui
import inary.cli.command as command
import inary.util as util
import optparse

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class InitNothing(command.PackageOp, metaclass=command.autocommand):
    __doc__ = _("""Do not anything.""")

    def __init__(self, args):
        super(InitNothing, self).__init__(args)

    name = (_("init"), "i")

    def options(self):
        pass

    def run(self):
        pass
