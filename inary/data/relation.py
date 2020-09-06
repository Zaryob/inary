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

# Inary Modules
import inary.db
import inary.version

# AutoXML Library
import inary.sxml.autoxml as autoxml


class Relation(metaclass=autoxml.autoxml):
    s_Package = [autoxml.String, autoxml.mandatory]
    a_version = [autoxml.String, autoxml.optional]
    a_versionFrom = [autoxml.String, autoxml.optional]
    a_versionTo = [autoxml.String, autoxml.optional]
    a_release = [autoxml.String, autoxml.optional]
    a_releaseFrom = [autoxml.String, autoxml.optional]
    a_releaseTo = [autoxml.String, autoxml.optional]

    def satisfies_relation(self, version, release):
        if self.version and version != self.version:
            return False
        else:
            v = inary.version.make_version(version)

            if self.versionFrom and \
                    v < inary.version.make_version(self.versionFrom):
                return False

            if self.versionTo and \
                    v > inary.version.make_version(self.versionTo):
                return False

        if self.release and release != self.release:
            return False
        else:
            r = int(release)

            if self.releaseFrom and r < int(self.releaseFrom):
                return False

            if self.releaseTo and r > int(self.releaseTo):
                return False

        return True


def installed_package_satisfies(relation):
    installdb = inary.db.installdb.InstallDB()
    pkg_name = relation.package
    if not installdb.has_package(pkg_name):
        return False
    else:
        pkg = installdb.get_package(pkg_name)
        return relation.satisfies_relation(pkg.version, pkg.release)
