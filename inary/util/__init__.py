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
from inary.util.strings import *
from inary.util.process import *
from inary.util.path import *
from inary.util.package import *
from inary.util.misc import *
from inary.util.kernel import *
from inary.util.filesystem_terminal import *
from inary.util.files import *
from inary.util.curses import *
import fcntl
import inary
import inary.errors
import inary.context as ctx

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)

        return cls.instance


def locked(func):
    """
    Decorator for synchronizing privileged functions
    """

    def wrapper(*__args, **__kw):
        try:
            lock = open(join_path(ctx.config.lock_dir(), 'inary'), 'w')
        except IOError:
            raise inary.errors.PrivilegeError(
                _("You have to be root for this operation."))

        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            ctx.locked = True
        except IOError:
            if not ctx.locked:
                raise inary.errors.AnotherInstanceError(
                    _("Another instance of Inary is running. Only one instance is allowed."))

        try:
            inary.db.invalidate_caches()
            ctx.ui.info(_('Invalidating database caches...'), verbose=True)
            ret = func(*__args, **__kw)
            ctx.ui.info(_('Updating database caches...'), verbose=True)
            inary.db.update_caches()
            return ret
        finally:
            ctx.locked = False
            lock.close()

    return wrapper
