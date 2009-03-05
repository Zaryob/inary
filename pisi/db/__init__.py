# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 - 2009, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import pisi

def reload():
    pisi.db.packagedb.PackageDB().reload()
    pisi.db.sourcedb.SourceDB().reload()
    pisi.db.componentdb.ComponentDB().reload()
