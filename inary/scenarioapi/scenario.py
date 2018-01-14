#!/usr/bin/env python3
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

from inary.scenarioapi.repoops import *
from inary.scenarioapi.inaryops import *
from inary.scenarioapi.constants import *

def let_repo_had(package, *args):
    repo_added_package(package, *args)
    repo_updated_index()

def let_inary_had(*args):
    url = os.path.join(os.getcwd(), consts.repo_url)
    inary_added_repo(consts.repo_name, url)
    packages = util.strlist(args).rstrip()
    os.system("inary -D%s install --ignore-dependency %s" % (consts.inary_db, packages))
