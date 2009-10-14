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

def get_option(opt):
    return config and config.get_option(opt)

# default UI is CLI
ui = None # not now

installdb = None
repodb = None

comar = None

initialized = False

#def register(_impl):
#    """ Register a UI implementation"""
#    ui = _impl
