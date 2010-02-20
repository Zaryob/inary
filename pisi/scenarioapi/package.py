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
import glob

from pisi.scenarioapi.pspec import Pspec
from pisi.scenarioapi.actions import Actions
from pisi.scenarioapi.constants import *
from pisi.scenarioapi.withops import *

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

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

    def create_pisi(self):
        os.system("pisi build %s -O %s > /dev/null 2>&1" % (consts.pspec_path, consts.repo_path))

    def create_package(self):
        pspec = Pspec(self.name, consts.pspec_path)
        pspec.set_source(consts.homepage, consts.summary % self.name,
                         consts.description % self.name, consts.license, self.partOf)
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

        self.create_pisi()

    def get_file_name(self):
        # use glob. there may be buildnos at the end of the package name
        pkg = consts.repo_path + self.name + "-" + \
              self.version + "-" + self.pspec.pspec.history[0].release

        found = glob.glob(pkg + consts.glob_pisis)
        if not found:
            raise Exception(_("No pisi package: %s* found.") % pkg)

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
        self.create_pisi()

if __name__ == "__main__":
    p = Package("w0rmux", [], [], "0.7")
    p.version_bump()
