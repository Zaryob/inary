# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 - 2007, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# global variables here

import signal

import pisi.constants
import pisi.signalhandler

const = pisi.constants.Constants()
sig = None

config = None

log = None

def set_option(opt, val):
    config.set_option(opt, val)

def get_option(opt):
    return config and config.get_option(opt)

# default UI is CLI
ui = None # not now

# stdout, stderr for PiSi API
stdout = None
stderr = None

dbenv = None
installdb = None
packagedb = None
repodb = None
sourcedb = None
filesdb = None
componentdb = None
invidx = None

comar = None
comar_sockname = None

initialized = False

# Bug #2879
# FIXME: Maybe we can create a simple rollback mechanism. There are other
# places which need this, too.
# this is needed in build process to clean after if something goes wrong.
build_leftover = None

#def register(_impl):
#    """ Register a UI implementation"""
#    ui = _impl

import bsddb3.db as db

# copy of DBShelve.txn_proc, the only difference is it doesn't need a shelf object
#FIXME: remove this redundancy, and move all this stuff to database.py
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
            except Exception, e:
                autotxn.abort()
                raise e
            autotxn.commit()
        else:
            retval = proc(None)
        return retval
    else:
        return proc(txn)

def disable_keyboard_interrupts():
    sig and sig.disable_signal(signal.SIGINT)

def enable_keyboard_interrupts():
    sig and sig.enable_signal(signal.SIGINT)

def keyboard_interrupt_disabled():
    return sig and sig.signal_disabled(signal.SIGINT)

def keyboard_interrupt_pending():
    return sig and sig.signal_pending(signal.SIGINT)
