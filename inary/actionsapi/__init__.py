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
#

import inary.context as ctx
import inary.errors

class Error(inary.errors.Error):
    pass

class Exception(inary.errors.Exception):
    pass

def error(msg):
    if ctx.config.get_option('ignore_action_errors'):
        ctx.ui.error(msg)
    else:
        raise Error(msg)
