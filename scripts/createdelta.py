#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

import os
import glob
import inary
import inary.util as util
from inary.version import Version
from inary.delta import create_delta_package

def minsandmaxes():

    packages = [os.path.basename(x).split(".inary")[0] for x in set(glob.glob("*.inary")) - set(glob.glob("*.delta.inary"))]

    versions = {}
    for file in packages:
        name, version = util.parse_package_name(file)
        versions.setdefault(name, []).append(Version(version))

    mins = {}
    maxs = {}
    for pkg in list(versions.keys()):
        mins[pkg] = min(versions[pkg])
        maxs[pkg] = max(versions[pkg])

    return mins, maxs

if __name__ == "__main__":

    mi, ma = minsandmaxes()
    for pkg in list(mi.keys()):
        old_pkg = "%s-%s.inary" % (pkg, str(mi[pkg]))
        new_pkg = "%s-%s.inary" % (pkg, str(ma[pkg]))
        name, version = util.parse_package_name(pkg)

        if not old_pkg == new_pkg:
        # skip if same 
            if not os.path.exists("%s-%s-%s.delta.inary" % (name, str(mi[pkg].build), str(ma[pkg].build))):
            # skip if delta exists
                print(("%s --> Min: %s Max: %s \n %s-%s-%s.delta.inary" % (pkg, old_pkg, new_pkg, name, str(mi[pkg].build), str(ma[pkg].build))))
                create_delta_package(old_pkg, new_pkg)
