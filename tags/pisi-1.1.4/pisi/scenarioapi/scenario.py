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

from pisi.scenarioapi.repoops import *
from pisi.scenarioapi.pisiops import *
from pisi.scenarioapi.constants import *

def let_repo_had(package, *args):
    repo_added_package(package, *args)
    repo_updated_index()

def let_pisi_had(*args):
    url = os.path.join(os.getcwd(), consts.repo_url)
    pisi_added_repo(consts.repo_name, url)
    packages = util.strlist(args).rstrip()
    os.system("pisi -D%s install --ignore-dependency %s" % (consts.pisi_db, packages))
