# -*- coding: utf-8 -*-
#
# Copyright (C) 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# Standart Python Libraries
import os

# Inary Modules
import inary.db
import inary.data
import inary.errors
import inary.package
import inary.context as ctx

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


def info(package, installed=False):
    if package.endswith(ctx.const.package_suffix):
        return info_file(package)
    else:
        metadata, files, repo = info_name(package, installed)
        return metadata, files


def info_file(package_fn):
    if not os.path.exists(package_fn):
        raise inary.errors.Error(
            _('File \"{}\" not found.').format(package_fn))

    package = inary.package.Package(package_fn)
    package.read()
    return package.metadata, package.files


def info_name(package_name, useinstalldb=False):
    """Fetch package information for the given package."""

    installdb = inary.db.installdb.InstallDB()
    packagedb = inary.db.packagedb.PackageDB()
    if useinstalldb:
        package = installdb.get_package(package_name)
        repo = None
    else:
        package, repo = packagedb.get_package_repo(package_name)

    metadata = inary.data.metadata.MetaData()
    metadata.package = package
    # FIXME: get it from sourcedb if available
    metadata.source = None
    # TODO: fetch the files from server if possible (wow, you maniac -- future
    # exa)
    if useinstalldb and installdb.has_package(package.name):
        try:
            files = installdb.get_files(package.name)
        except inary.errors.Error as e:
            ctx.ui.warning(e)
            files = None
    else:
        files = None
    return metadata, files, repo
