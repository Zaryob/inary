#!/usr/bin/python
#-*- coding: utf-8 -*-
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
#

import os
import inary.util as util
from inary.scenarioapi.constants import *

def inary_upgraded(*args):
    packages = util.strlist(args).rstrip()
    os.system("inary -D{0} upgrade {1}".format(consts.inary_db, packages))

def inary_info(package):
    os.system("inary -D{0} info {1}".format(consts.inary_db, package))

def inary_removed(*args):
    packages = util.strlist(args).rstrip()
    os.system("inary -D{0} remove {1}".format(consts.inary_db, packages))

def inary_added_repo(name, url):
    os.system("inary -D{0} add-repo -y {1} {2}".format(consts.inary_db, name, url))

def inary_updated_repo():
    os.system("inary -D{0} update-repo".fotmat(consts.inary_db))

def inary_installed(*args):
    packages = util.strlist(args).rstrip()
    os.system("inary -D{0} install {1}".format(consts.inary_db, packages))

def inary_reinstalled(package):
    os.system("inary -D{0} install --reinstall {1}".format(consts.inary_db, package))
