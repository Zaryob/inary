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

# Standart Python Libraries
import os

# Inary Modules
import inary.db
import inary.util
import inary.context as ctx

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

# These guys will change due to depmod calls.
_blessed_kernel_borks = [
    "modules.alias",
    "modules.alias.bin",
    "modules.dep",
    "modules.dep.bin",
    "modules.symbols",
    "modules.symbols.bin",
]


def ignorance_is_bliss(f):
    """ Too many complaints about things that are missing. """
    p = f
    if not p.startswith("/"):
        p = "/{}".format(f)

    pbas = os.path.basename(p)
    p = p.replace("/lib64/", "/lib/")

    # Ignore kernel depmod changes?
    if p.startswith("/lib/modules"):
        if pbas in _blessed_kernel_borks:
            return True

    if p.endswith(".pyc"):
        # ignore python compiled file changes
        return True


def file_corrupted(pfile):
    path = os.path.join(ctx.config.dest_dir(), pfile.path)
    if os.path.islink(path):
        if inary.util.sha1_data(inary.util.read_link(path)) != pfile.hash:
            return True
    else:
        try:
            if inary.util.sha1_file(path) != pfile.hash:
                return True
        except inary.util.FilePermissionDeniedError as e:
            raise e
    return False


def check_files(files, check_config=False):
    results = {
        'missing': [],
        'corrupted': [],
        'denied': [],
        'config': [],
    }

    for f in files:
        if not check_config and f.type == "config":
            continue
        if not f.hash:
            continue
        if ignorance_is_bliss(f.path):
            continue

        is_file_corrupted = False

        path = os.path.join(ctx.config.dest_dir(), f.path)
        if os.path.lexists(path):
            try:
                is_file_corrupted = file_corrupted(f)

            except inary.util.FilePermissionDeniedError:
                # Can't read file, probably because of permissions, skip
                results['denied'].append(f.path)

            else:
                if is_file_corrupted:
                    # Detect file type
                    if f.type == "config":
                        results['config'].append(f.path)
                    else:
                        results['corrupted'].append(f.path)

        else:
            # Shipped file doesn't exist on the system
            results['missing'].append(f.path)

    return results


def check_config_files(package):
    config_files = inary.db.installdb.InstallDB().get_config_files(package)
    return check_files(config_files, True)


def check_package_files(package):
    files = inary.db.installdb.InstallDB().get_files(package).list
    return check_files(files)


def check(package, config=False):
    """
    Returns a dictionary that contains a list of both corrupted and missing files
    @param package: name of the package to be checked
    @param config: _only_ check the config files of the package, default behaviour is to check all the files
    of the package but the config files
    """
    if config:
        return check_config_files(package)
    else:
        return check_package_files(package)
