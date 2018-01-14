#!/usr/bin/python
#-*- coding: utf-8 -*-
#
# Copyright (C) 2016 - 2017, Suleyman POYRAZ (AquilaNipalensis) 
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import os
import inary.util as util
from inary.scenarioapi.constants import *

def inary_upgraded(*args):
    packages = util.strlist(args).rstrip()
    os.system("inary -D%s upgrade %s" % (consts.inary_db, packages))

def inary_info(package):
    os.system("inary -D%s info %s" % (consts.inary_db, package))

def inary_removed(*args):
    packages = util.strlist(args).rstrip()
    os.system("inary -D%s remove %s" % (consts.inary_db, packages))

def inary_added_repo(name, url):
    os.system("inary -D%s add-repo -y %s %s" % (consts.inary_db, name, url))

def inary_updated_repo():
    os.system("inary -D%s update-repo" % consts.inary_db)

def inary_installed(*args):
    packages = util.strlist(args).rstrip()
    os.system("inary -D%s install %s" % (consts.inary_db, packages))

def inary_reinstalled(package):
    os.system("inary -D%s install --reinstall %s" % (consts.inary_db, package))

