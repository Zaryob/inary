# -*- coding: utf-8 -*-
#
# Copyright (C) 2008, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

import os
import pisi
import pisi.context as ctx

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

def file_corrupted(pfile):
    if os.path.islink("/%s" % pfile.path):
        if pisi.util.sha1_data(os.readlink("/%s" % pfile.path)) != pfile.hash:
            return True
    else:
        if pisi.util.sha1_file("/%s" % pfile.path) != pfile.hash:
            return True
    return False

def check_files(files, check_config=False):
    results = {'missing':[],'corrupted':[]}
    for f in files:
        if not check_config and f.type == "config":
            continue
        if not f.hash:
            continue
        ctx.ui.info(_("Checking /%s ") % f.path, noln=True, verbose=True)
        if os.path.lexists("/%s" % f.path):
            if file_corrupted(f):
                if f.type == "config":
                    msg = _("\nChanged config file: %s")
                else:
                    msg = _("\nCorrupt file: %s")
                ctx.ui.error(msg % ("/%s" %f.path))
                results['corrupted'].append(f.path)
            else:
                ctx.ui.info(_("OK"), verbose=True)
        else:
            results['missing'].append(f.path)
    return results

def check_config_files(package):
    config_files = pisi.db.installdb.InstallDB().get_config_files(package)
    return check_files(config_files, True)

def check_package_files(package):
    files = pisi.db.installdb.InstallDB().get_files(package).list
    return check_files(files)

def check_package(package, config=False):
    if config:
        return check_config_files(package)
    else:
        return check_package_files(package)
