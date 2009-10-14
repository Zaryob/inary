#!/usr/bin/python
#-*- coding: utf-8 -*-
#
# Copyright (C) 2006, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import os
import pisi.util as util
from pisi.scenarioapi.constants import *

def pisi_upgraded(*args):
    packages = util.strlist(args).rstrip()
    os.system("pisi -D%s upgrade %s" % (consts.pisi_db, packages))

def pisi_info(package):
    os.system("pisi -D%s info %s" % (consts.pisi_db, package))

def pisi_removed(*args):
    packages = util.strlist(args).rstrip()
    os.system("pisi -D%s remove %s" % (consts.pisi_db, packages))

def pisi_added_repo(name, url):
    os.system("pisi -D%s add-repo -y %s %s" % (consts.pisi_db, name, url))

def pisi_updated_repo():
    os.system("pisi -D%s update-repo" % consts.pisi_db)

def pisi_installed(*args):
    packages = util.strlist(args).rstrip()
    os.system("pisi -D%s install %s" % (consts.pisi_db, packages))

def pisi_reinstalled(package):
    os.system("pisi -D%s install --reinstall %s" % (consts.pisi_db, package))

