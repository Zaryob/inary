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

"""conflict analyzer"""

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.context as ctx
import pisi.version
import pisi.pxml.autoxml as autoxml
import pisi.db.itembyrepodb

class Conflict:

    __metaclass__ = autoxml.autoxml

    s_Package = [autoxml.String, autoxml.mandatory]
    a_version = [autoxml.String, autoxml.optional]
    a_versionFrom = [autoxml.String, autoxml.optional]
    a_versionTo = [autoxml.String, autoxml.optional]
    a_release = [autoxml.String, autoxml.optional]
    a_releaseFrom = [autoxml.String, autoxml.optional]
    a_releaseTo = [autoxml.String, autoxml.optional]

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

    def conflicts(self, pkg_name, version, release):
        """determine if a package ver. conflicts with given conflicting spec"""
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

def installed_package_conflicts(confinfo):
    """determine if an installed package in *repository* conflicts with
given conflicting spec"""
    pkg_name = confinfo.package
    if not ctx.installdb.is_installed(pkg_name):
        return False
    else:
        pkg = api.get_installed_package(pkg_name)
        (version, release) = (pkg.version, pkg.release)
        return confinfo.conflicts(pkg_name, version, release)

def package_conflicts(pkg, confs):
    for c in confs:
        if pkg.name == c.package and c.conflicts(pkg.name, pkg.version, pkg.release):
            return c

    return None
