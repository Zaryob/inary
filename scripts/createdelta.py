#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, 2006 TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

import os
import glob
import pisi
import pisi.util as util
from pisi.version import Version
from pisi.delta import create_delta_package

def minsandmaxes():

    packages = map(lambda x: os.path.basename(x).split(".pisi")[0], set(glob.glob("*.pisi")) - set(glob.glob("*.delta.pisi")))

    versions = {}
    for file in packages:
        name, version = util.parse_package_name(file)
        versions.setdefault(name, []).append(Version(version))

    mins = {}
    maxs = {}
    for pkg in versions.keys():
        mins[pkg] = min(versions[pkg])
        maxs[pkg] = max(versions[pkg])

    return mins, maxs

if __name__ == "__main__":

    mi, ma = minsandmaxes()
    for pkg in mi.keys():
        old_pkg = "%s-%s.pisi" % (pkg, str(mi[pkg]))
        new_pkg = "%s-%s.pisi" % (pkg, str(ma[pkg]))
        name, version = util.parse_package_name(pkg)

        if not old_pkg == new_pkg:
        # skip if same 
            if not os.path.exists("%s-%s-%s.delta.pisi" % (name, str(mi[pkg].build), str(ma[pkg].build))):
            # skip if delta exists
                print "%s --> Min: %s Max: %s \n %s-%s-%s.delta.pisi" % (pkg, old_pkg, new_pkg, name, str(mi[pkg].build), str(ma[pkg].build))
                create_delta_package(old_pkg, new_pkg)
