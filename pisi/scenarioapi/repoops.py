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
# Authors:  Faik Uygur <faik@pardus.org.tr>

import os

from pisi.scenarioapi.package import Package
from pisi.scenarioapi.withops import *
from pisi.scenarioapi.constants import *

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

repodb = {}

def repo_added_package(package, *args):
    if repodb.has_key(package):
        raise Exception(_("Repo already has package named %s.") % package)

    dependencies = None
    conflicts = None
    
    if args:
        for with in args:
            if with.types == CONFLICT and with.action == INIT:
                conflicts = with.pkgs
            
            if with.types == DEPENDENCY and with.action == INIT:
                dependencies = with.pkgs

    repodb[package] = Package(package, dependencies, conflicts)

def repo_removed_package(package):
    if not repodb.has_key(package):
        raise Exception(_("Repo does not have package named %s.") % package)

    os.unlink(os.path.join(consts.repo_path, repodb[package].get_file_name()))
    del repodb[package]

def repo_version_bumped(package, *args):
    if not repodb.has_key(package):
        raise Exception(_("Repo does not have package named %s.") % package)

    old_file = repodb[package].get_file_name()
    repodb[package].version_bump(*args)
    os.unlink(os.path.join(consts.repo_path, old_file))

def repo_updated_index():
    cur = os.getcwd()
    path = os.path.join(cur, consts.repo_path)
    os.chdir(consts.repo_path)
    os.system("pisi index %s >/dev/null 2>&1" % path)
    os.chdir(cur)

def repo_get_url():
    return "."
