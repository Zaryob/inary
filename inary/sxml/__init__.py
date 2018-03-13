# -*- coding: utf-8 -*-
#
#
# Old author: Copyright (C) 2005 - 2011, Tubitak/UEKAE 
#
# Copyright (C) 2017 - 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import sys
import locale

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary

class Error(inary.Error):
    pass
