# -*- coding: utf-8 -*-
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

from . import fetcher

import gettext

__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary

import inary.atomicoperations
import inary.blacklist
import inary.config
import inary.context as ctx

# DataFile Libraries
import inary.data
import inary.data.index
import inary.data.metadata
import inary.data.pgraph

# DataBase Libraries
import inary.db.componentdb
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

# Operation Libraries
import inary.operations.build
import inary.operations.check
import inary.operations.emerge
import inary.operations.info
import inary.operations.install
import inary.operations.history
import inary.operations.helper
import inary.operations.remove
import inary.operations.repository
import inary.operations.search
import inary.operations.upgrade

import inary.uri
import inary.util

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


# The following are INARY operations which constitute the INARY API
# Within functions
from inary.analyzer.conflict import calculate_conflicts
from inary.db.filesdb import rebuild_db
from inary.data.index import index
from inary.data.pgraph import package_graph
from inary.fetcher import fetch
from inary.operations.build import build, build_until
from inary.operations.check import check
from inary.operations.emerge import emerge
from inary.operations.helper import calculate_download_sizes, calculate_free_space_needed, get_package_requirements
from inary.operations.history import takeback, get_takeback_plan, snapshot
from inary.operations.info import info
from inary.operations.install import install, get_install_order
from inary.operations.remove import remove, get_remove_order
from inary.operations.repository import *
from inary.operations.upgrade import upgrade, get_upgrade_order, get_base_upgrade_order
from inary.operations.search import *
