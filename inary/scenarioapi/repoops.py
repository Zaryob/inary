#!/usr/bin/env python3
#-*- coding: utf-8 -*-
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

import os

from inary.scenarioapi.package import Package
from inary.scenarioapi.withops import *
from inary.scenarioapi.constants import *

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

repodb = {}

def repo_added_package(package, *args):
    if package in repodb:
        raise Exception(_("Repo already has package named {}.").format(package))

    version = "1.0"
    partOf = "None"
    dependencies = []
    conflicts = []

    for _with in args:
        if _with.types == CONFLICT and _with.action == INIT:
            conflicts = _with.data

        if _with.types == DEPENDENCY and _with.action == INIT:
            dependencies = _with.data

        if _with.types == VERSION and _with.action == INIT:
            version = _with.data

        if _with.types == PARTOF and _with.action == INIT:
            partOf = _with.data

    repodb[package] = Package(package, dependencies, conflicts, ver=version, partOf=partOf)

def repo_removed_package(package):
    if package not in repodb:
        raise Exception(_("Repo does not have package named {}.").format(package))

    os.unlink(os.path.join(consts.repo_path, repodb[package].get_file_name()))
    del repodb[package]

def repo_version_bumped(package, *args):
    if package not in repodb:
        raise Exception(_("Repo does not have package named {}.").format(package))

    old_file = repodb[package].get_file_name()
    repodb[package].version_bump(*args)
    os.unlink(os.path.join(consts.repo_path, old_file))

def repo_updated_index():
    cur = os.getcwd()
    path = os.path.join(cur, consts.repo_path)
    os.chdir(consts.repo_path)
    os.system("inary index --skip-signing {} >/dev/null 2>&1".format(path))
    os.chdir(cur)

def repo_get_url():
    return "."
