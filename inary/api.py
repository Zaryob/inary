# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 - 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

import os
import re
from . import fetcher

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary
import inary.atomicoperations
import inary.blacklist
import inary.config
import inary.context as ctx
import inary.data
import inary.data.index
import inary.data.metadata
import inary.data.pgraph as pgraph
import inary.db.packagedb
import inary.db.repodb
import inary.db.filesdb
import inary.db.installdb
import inary.db.historydb
import inary.db.sourcedb
import inary.db.componentdb
import inary.db.groupdb
import inary.errors
import inary.file
from inary.reactor import *
import inary.operations.build
import inary.operations.check
import inary.operations.emerge
import inary.operations.install
import inary.operations.history
import inary.operations.helper
import inary.operations.remove
import inary.operations.upgrade
import inary.uri
import inary.util

def set_scom(enable):
    """
    Set scom usage
    False means no preremove and postinstall scripts will be run
    @param enable: Flag indicating scom usage
    """
    ctx.scom = enable

def set_scom_updated(updated):
    """
    Set scom package update status
    @param updated: True if COMAR package is updated, else False
    """
    ctx.scom_updated = updated

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
