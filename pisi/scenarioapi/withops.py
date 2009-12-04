#!/usr/bin/python
#-*- coding: utf-8 -*-
#
# Copyright (C) 2006, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

ADDED, REMOVED, INIT = range(3)
PARTOF, VERSION, CONFLICT, DEPENDENCY, REQUIRES = range(5)

class With:
    def __init__(self):
        pass

def with_action(types, action, data):
    w = With()
    w.types = types
    w.action = action
    w.data = data
    return w

def with_partof(partof):
    return with_action(PARTOF, INIT, partof)

def with_version(version):
    return with_action(VERSION, INIT, version)

def with_conflicts(*cons):
    return with_action(CONFLICT, INIT, cons)

def with_requiring_actions(*action):
    return with_action(REQUIRES, ADDED, action)

def with_dependencies(*deps):
    return with_action(DEPENDENCY, INIT, deps)

def with_added_conflicts(*cons):
    return with_action(CONFLICT, ADDED, cons)

def with_removed_conflicts(*cons):
    return with_action(CONFLICT, REMOVED, cons)

def with_added_dependencies(*deps):
    return with_action(DEPENDENCY, ADDED, deps)

def with_removed_dependencies(*deps):
    return with_action(DEPENDENCY, REMOVED, deps)

def with_added_conflict(package, **kw):
    assert len(kw) <= 1

    if not len(kw):
        return with_action(CONFLICT, ADDED, [package])

    if (kw.has_key("versionFrom") or
        kw.has_key("versionTo") or
        kw.has_key("version") or
        kw.has_key("releaseFrom") or
        kw.has_key("releaseTo") or
        kw.has_key("release")):
        return with_action(CONFLICT, ADDED, [kw, package])

    # pass other keywords.
    return with_action(CONFLICT, ADDED, [package])

def with_added_dependency(package, **kw):
    assert len(kw) <= 1

    if not len(kw):
        return with_action(DEPENDENCY, ADDED, [package])

    if (kw.has_key("versionFrom") or
        kw.has_key("versionTo") or
        kw.has_key("version") or
        kw.has_key("releaseFrom") or
        kw.has_key("releaseTo") or
        kw.has_key("release")):
        return with_action(DEPENDENCY, ADDED, [kw, package])

    # pass other keywords.
    return with_action(DEPENDENCY, ADDED, [package])
