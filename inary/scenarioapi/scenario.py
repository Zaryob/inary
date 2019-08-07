#!/usr/bin/env python3
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
    os.system("inary -D{0} install --ignore-dependency {1}".format(consts.inary_db, packages))
