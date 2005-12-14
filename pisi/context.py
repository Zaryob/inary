# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# Context module.

# Authors: Baris Metin <baris@uludag.org.tr
#          Eray Ozkural <eray@uludag.org.tr>

# global variables here

import pisi.constants

const = pisi.constants.Constants()

config = None

use_mdom = False

def get_option(opt):
    return config and config.get_option(opt)

# default UI is CLI
ui = None # not now

dbenv = None
installdb = None
repodb = None
invidx = None

comar = None

initialized = False

#def register(_impl):
#    """ Register a UI implementation"""
#    ui = _impl

import bsddb3.db as db

def txn_proc(proc, txn = None):
    # can be used to txn protect a method automatically
    if not txn:
        if dbenv:
            autotxn = dbenv.txn_begin()
            try:
                retval = proc(autotxn)
            except db.DBError, e:
                autotxn.abort()
                raise e
            autotxn.commit()
        else:
            retval = proc(None)
        return retval
    else:
        return proc(txn)
