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
import struct
import termios
import fcntl
import sys
import os
import inary
import inary.errors
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

######################
# Terminal functions #
######################


def get_terminal_size():
    try:
        ret = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, "1234")
    except IOError:
        rows = int(os.environ.get("LINES", 25))
        cols = int(os.environ.get("COLUMNS", 80))
        return rows, cols

    return struct.unpack("hh", ret)


def xterm_title(message):
    """Set message as console window title."""
    if "TERM" in os.environ and sys.stderr.isatty():
        terminalType = os.environ["TERM"]
        for term in ["xterm", "Eterm", "aterm",
                     "rxvt", "screen", "kterm", "rxvt-unicode"]:
            if terminalType.startswith(term):
                sys.stderr.write("\x1b]2;" + str(message) + "\x07")
                sys.stderr.flush()
                break


def xterm_title_reset():
    """Reset console window title."""
    if "TERM" in os.environ:
        xterm_title("")
