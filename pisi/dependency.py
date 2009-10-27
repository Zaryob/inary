# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 - 2007, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

"""dependency analyzer"""

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.relation
import pisi.db

class Dependency(pisi.relation.Relation):
    def __str__(self):
        s = self.package
        if self.versionFrom:
            s += _(" version >= ") + self.versionFrom
        if self.versionTo:
            s += _(" version <= ") + self.versionTo
        if self.version:
            s += _(" version ") + self.version
        if self.releaseFrom:
            s += _(" release >= ") + self.releaseFrom
        if self.releaseTo:
            s += _(" release <= ") + self.releaseTo
        if self.release:
            s += _(" release ") + self.release
        return s

    def name(self):
        return self.package

    def satisfied_by_dict_repo(self, dict_repo):
        if not dict_repo.has_key(self.package):
            return False
        else:
            pkg = dict_repo[self.package]
            return self.satisfies_relation(pkg.version, pkg.release)

    def satisfied_by_installed(self):
        return pisi.relation.installed_package_satisfies(self)

    def satisfied_by_repo(self):
        packagedb = pisi.db.packagedb.PackageDB()
        if not packagedb.has_package(self.package):
            return False
        else:
            pkg = packagedb.get_package(self.package)
            return self.satisfies_relation(pkg.version, pkg.release)

    # Added for AnyDependency, single Dependency always returns False
    def satisfied_by_any_installed_other_than(self, package):
        return False
