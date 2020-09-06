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

import inary.context as ctx
import inary.signalhandler


def set_userinterface(ui):
    """
    Set the user interface where the status information will be send
    @param ui: User interface
    """
    ctx.ui = ui


def set_io_streams(stdout=None, stderr=None):
    """
    Set standart i/o streams
    Used by Buildfarm
    @param stdout: Standart output
    @param stderr: Standart input
    """
    if stdout:
        ctx.stdout = stdout
    if stderr:
        ctx.stderr = stderr


def set_dbus_sockname(sockname):
    """
    Set dbus socket file
    Used by YALI
    @param sockname: Path to dbus socket file
    """
    ctx.dbus_sockname = sockname


def set_dbus_timeout(timeout):
    """
    Set dbus timeout
    Used by YALI
    @param timeout: Timeout in seconds
    """
    ctx.dbus_timeout = timeout


def set_signal_handling(enable):
    """
    Enable signal handling. Signal handling in inary mostly used for disabling keyboard interrupts
    in critical paths.
    Used by YALI
    @param enable: Flag indicating signal handling usage
    """
    if enable:
        ctx.sig = inary.signalhandler.SignalHandler()
    else:
        ctx.sig = None


def set_options(options):
    """
    Set various options of inary
    @param options: option set

       >>> options = inary.config.Options()

           options.destdir     # inary destination directory where operations will take effect
           options.username    # username that for reaching remote repository
           options.password    # password that for reaching remote repository
           options.debug       # flag controlling debug output
           options.verbose     # flag controlling verbosity of the output messages
           options.output_dir  # build and delta operations package output directory
    """
    ctx.config.set_options(options)
