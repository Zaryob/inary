# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2020, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

"""dependency analyzer"""

import inary.sxml.autoxml as autoxml
import inary.data.relation as relation
from inary.db.packagedb import PackageDB

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class Dependency(relation.Relation, metaclass=autoxml.autoxml):
    a_type = [autoxml.String, autoxml.optional]

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
        if self.type:
            s += " (" + self.type + ")"
        return s

    def name(self):
        return self.package

    def satisfied_by_dict_repo(self, dict_repo):

        if self.package not in dict_repo:
            return False
        else:
            pkg = dict_repo[self.package]
            return self.satisfies_relation(pkg.version, pkg.release)

    def satisfied_by_installed(self):
        return relation.installed_package_satisfies(self)

    def satisfied_by_repo(self, packagedb=None):
        if not packagedb:
            packagedb = PackageDB()

        if not packagedb.has_package(self.package):
            return False
        else:
            pkg = packagedb.get_package(self.package)
            return self.satisfies_relation(pkg.version, pkg.release)

    # Added for AnyDependency, single Dependency always returns False
    def satisfied_by_any_installed_other_than(self, package):
        pass
