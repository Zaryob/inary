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

def invalidate_caches():
    # Invalidates pisi caches in use and forces to re-fill caches from disk when needed
    for db in [packagedb.PackageDB(), sourcedb.SourceDB(), componentdb.ComponentDB(),
               installdb.InstallDB(), historydb.HistoryDB(), groupdb.GroupDB(), repodb.RepoDB()]:
        db.invalidate()

def flush_caches():
    # Invalidate and flush caches to re-generate them when needed
    for db in [packagedb.PackageDB(), sourcedb.SourceDB(),
               componentdb.ComponentDB(), groupdb.GroupDB()]:
        db.invalidate()
        db.cache_flush()

def update_caches():
    # Updates ondisk caches
    for db in [packagedb.PackageDB(), sourcedb.SourceDB(), componentdb.ComponentDB(),
               installdb.InstallDB(), groupdb.GroupDB()]:
        if db.is_initialized():
            db.cache_save()

def regenerate_caches():
    flush_caches()
    # Force cache regeneration
    for db in [packagedb.PackageDB(), sourcedb.SourceDB(),
               componentdb.ComponentDB(), groupdb.GroupDB()]:
        db.cache_regenerate()
