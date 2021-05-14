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

# INARY version

import atexit
import importlib
import logging
import logging.handlers
import os
import sys

__version__ = "1.5.0"

__all__ = ['api', 'configfile', 'db', 'util', '_cleanup']

import inary.api
import inary.config
import inary.settings
import inary.context as ctx


def init_logging():
    log_dir = os.path.join(ctx.config.dest_dir(), ctx.config.log_dir())
    if os.access(log_dir, os.W_OK) and "distutils.core" not in sys.modules:
        handler = logging.handlers.RotatingFileHandler(
            '{}/inary.log'.format(log_dir))
        formatter = logging.Formatter(
            '%(asctime)-12s:  %(name)s(%(module)s:%(lineno)4d)  %(levelname)s  %(message)s')
        handler.setFormatter(formatter)
        ctx.log = logging.getLogger('inary')
        ctx.log.addHandler(handler)
        ctx.loghandler = handler
        ctx.log.setLevel(logging.DEBUG)


def _cleanup():
    """Close the database cleanly and do other cleanup."""
    ctx.disable_keyboard_interrupts()
    if ctx.log:
        ctx.loghandler.flush()
        ctx.log.removeHandler(ctx.loghandler)

    #    filesdb = inary.db.filesdb.FilesDB()
    #    if filesdb.is_initialized():
    #        filesdb.close()

    if ctx.build_leftover and os.path.exists(ctx.build_leftover):
        os.unlink(ctx.build_leftover)

    ctx.ui.close()
    ctx.enable_keyboard_interrupts()


# we need umask 0x022 (0x027 may broke so we need force 0x022)
os.umask(18)

# Hack for inary to work with non-patched Python. inary needs
# lots of work for not doing this.
importlib.reload(sys)

atexit.register(_cleanup)

ctx.config = inary.config.Config()
init_logging()
