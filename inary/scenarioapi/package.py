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
import glob

from inary.scenarioapi.pspec import Pspec
from inary.scenarioapi.actions import Actions
from inary.scenarioapi.constants import *
from inary.scenarioapi.withops import *

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

class Package:
    def __init__(self, name, deps = [], cons = [], date = "2006-18-18", ver = "1.0", partOf="None"):
        self.name = name
        self.dependencies = deps
        self.conflicts = cons
        self.version = ver
        self.date = date
        self.partOf = partOf
        self.pspec = None
        self.actions = None
        self.create_package()

    def create_inary(self):
        os.system("inary build {0} -O {1} > /dev/null 2>&1".format(consts.pspec_path, consts.repo_path))

    def create_package(self):
        pspec = Pspec(self.name, consts.pspec_path)
        pspec.set_source(consts.homepage, consts.summary.format(self.name),
                         consts.description.format(self.name), consts.license, self.partOf)
        pspec.set_packager(consts.packager_name, consts.packager_email)
        pspec.add_archive(consts.skel_sha1sum, consts.skel_type, consts.skel_uri)
        pspec.set_package(self.dependencies, self.conflicts)
        pspec.add_file_path(consts.skel_bindir, consts.skel_dirtype)
        pspec.set_history(self.date, self.version)

        actions = Actions(self.name, consts.actionspy_path)

        self.pspec = pspec
        self.actions = actions
        self.pspec.write()
        self.actions.write()

        self.create_inary()

    def get_file_name(self):
        # use glob. there may be buildnos at the end of the package name
        pkg = consts.repo_path + self.name + "-" + \
              self.version + "-" + self.pspec.pspec.history[0].release

        found = glob.glob(pkg + consts.glob_inarys)
        if not found:
            raise Exception(_("No inary package: {}* found.").format(pkg))

        return os.path.basename(found[0])

    def version_bump(self, *args):
        for _with in args:
            if _with.types == CONFLICT and _with.action == ADDED:
                self.pspec.add_conflicts(_with.data)

            if _with.types == REQUIRES and _with.action == ADDED:
                self.pspec.add_requires(_with.data)

            if _with.types == CONFLICT and _with.action == REMOVED:
                self.pspec.remove_conflicts(_with.data)

            if _with.types == DEPENDENCY and _with.action == ADDED:
                self.pspec.add_dependencies(_with.data)

            if _with.types == DEPENDENCY and _with.action == REMOVED:
                self.pspec.remove_dependencies(_with.data)

            if _with.types == VERSION and _with.action == INIT:
                self.version = _with.data

        self.pspec.update_history(self.date, self.version)

        self.pspec.write()
        self.actions.name = self.name
        self.actions.write()
        self.create_inary()

if __name__ == "__main__":
    p = Package("w0rmux", [], [], "0.7")
    p.version_bump()
