# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE (Licensed with GPLv2)
# More details about GPLv2, please read the COPYING.OLD file.
#
# Copyright (C) 2016 - 2019, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# Please read the COPYING file.
#

# global variables here

import signal

import inary.constants
import inary.signalhandler
import inary.ui

const = inary.constants.Constants()
sig = inary.signalhandler.SignalHandler()

config = None

log = None
loghandler = None
# used for bug #10568
locked = False


def set_option(opt, val):
    config.set_option(opt, val)


def get_option(opt):
    return config and config.get_option(opt)


ui = inary.ui.UI()

# stdout, stderr for INARY API
stdout = None
stderr = None

scom = True
scom_updated = False
dbus_sockname = None
dbus_timeout = 60 * 60  # in seconds

# Bug #2879
# FIXME: Maybe we can create a simple rollback mechanism. There are other
# places which need this, too.
# this is needed in build process to clean after if something goes wrong.
build_leftover = None


def disable_keyboard_interrupts():
    sig and sig.disable_signal(signal.SIGINT)


def enable_keyboard_interrupts():
    sig and sig.enable_signal(signal.SIGINT)


def keyboard_interrupt_disabled():
    return sig and sig.signal_disabled(signal.SIGINT)


def keyboard_interrupt_pending():
    return sig and sig.signal_pending(signal.SIGINT)


filesdb = None
