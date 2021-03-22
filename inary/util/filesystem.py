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

"""misc. utility functions, including filesystem utils"""

# Inary Modules
import os
import inary.context as ctx

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

########################
# Filesystem functions #
########################


def fs_sync():
    if ctx.config.values.general.fs_sync:
        ctx.ui.debug(
            _("Filesystem syncing (It wouldn't be run whether nosync set with kernel parameters)"))
        os.sync()
