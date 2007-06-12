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

import pisi.relation

""" Conflict relation """
class Conflict(pisi.relation.Relation):
    pass

def installed_package_conflicts(confinfo):
    """determine if an installed package in *repository* conflicts with
given conflicting spec"""
    return pisi.relation.installed_package_satisfies(confinfo)

def package_conflicts(pkg, confs):
    for c in confs:
        if pkg.name == c.package and c.satisfies_relation(pkg.name, pkg.version, pkg.release):
            return c

    return None
