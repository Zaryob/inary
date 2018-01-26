# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 - 2017, Suleyman POYRAZ (Zaryob) 
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

class Actions:

    template = """
from inary.actionsapi import inarytools

WorkDir = "skeleton"

def install():
    inarytools.dobin("skeleton.py")
    inarytools.rename("/usr/bin/skeleton.py", "{}")
"""

    def __init__(self, name, filepath):
        self.name = name
        self.filepath = filepath

    def write(self):
        open(self.filepath, "w").write(self.template.format(self.name))
