# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE (Licensed with GPLv2)
# More details about GPLv2, please read the COPYING.OLD file.
#
# Copyright (C) 2016 - 2019, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# Please read the COPYING file.
#

import fnmatch
import os

import inary.db


def exclude_from(packages, exfrom):
    if not os.path.exists(exfrom):
        return packages

    patterns = []
    if os.path.exists(exfrom):
        for line in open(exfrom).readlines():
            if not line.startswith('#') and not line == '\n':
                patterns.append(line.strip())
        if patterns:
            return exclude(packages, patterns)

    return packages


def exclude(packages, patterns):
    packages = set(packages)
    componentdb = inary.db.componentdb.ComponentDB()

    for pattern in patterns:
        # match pattern in package names
        match = fnmatch.filter(packages, pattern)
        packages -= set(match)

        if not match:
            # match pattern in component names
            for compare in fnmatch.filter(componentdb.list_components(), pattern):
                packages -= set(componentdb.get_union_packages(compare, walk=True))

    return list(packages)
