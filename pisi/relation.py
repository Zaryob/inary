# -*- coding: utf-8 -*-
#
# Copyright (C) 2007, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.context as ctx
import pisi.version
import pisi.pxml.autoxml as autoxml
import pisi.db.itembyrepodb

class Relation:

    __metaclass__ = autoxml.autoxml

    s_Package = [autoxml.String, autoxml.mandatory]
    a_version = [autoxml.String, autoxml.optional]
    a_versionFrom = [autoxml.String, autoxml.optional]
    a_versionTo = [autoxml.String, autoxml.optional]
    a_release = [autoxml.String, autoxml.optional]
    a_releaseFrom = [autoxml.String, autoxml.optional]
    a_releaseTo = [autoxml.String, autoxml.optional]

    def satisfies_relation(self, pkg_name, version, release):
        ret = True
        v = pisi.version.Version(version)
        if self.version:
            ret &= v == pisi.version.Version(self.version)
        if self.versionFrom:
            ret &= v >= pisi.version.Version(self.versionFrom)
        if self.versionTo:
            ret &= v <= pisi.version.Version(self.versionTo)
        r = pisi.version.Version(release)
        if self.release:
            ret &= r == pisi.version.Version(self.release)
        if self.releaseFrom:
            ret &= r >= pisi.version.Version(self.releaseFrom)
        if self.releaseTo:
            ret &= r <= pisi.version.Version(self.releaseTo)
        return ret

def installed_package_satisfies(relation):
    pkg_name = relation.package
    if not ctx.installdb.is_installed(pkg_name):
        return False
    else:
        pkg = ctx.packagedb.get_package(pkg_name, pisi.db.itembyrepodb.installed)
        (version, release) = (pkg.version, pkg.release)
        return relation.satisfies_relation(pkg_name, version, release)
