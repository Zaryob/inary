#!/usr/bin/env python
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

#
# Install script for tengis.
#

import os
import shutil
from distutils.core import setup
from distutils.command.install import install

PISI_VERSION = "0.1"

def getRevision():
    import os
    try:
        p = os.popen("svn info 2> /dev/null")
        for line in p.readlines():
            line = line.strip()
            if line.startswith("Revision:"):
                return line.split(":")[1].strip()
    except:
        pass

    # doesn't working in a Subversion directory
    return None

def getVersion():
    rev = getRevision()
    if rev:
        return "-r".join([PISI_VERSION, rev])
    else:
        return PISI_VERSION

class InstallPisi(install):
    def run(self):
        install.run(self)
        # FIXME: refactor this into a generic i18n function
        # and take po names and install dir from options
        os.popen("msgfmt po/tr.po -o po/tr.mo")
        shutil.copy("po/tr.mo", "/usr/share/locale/tr/LC_MESSAGES/pisi.mo")

setup(name="pisi",
    version= getVersion(),
    description="PISI (Packages Installed Successfully as Intended)",
    long_description="PISI is the package management system of Pardus Linux.",
    license="GNU GPL2",
    author="Pardus Developers",
    author_email="pisi@uludag.org.tr",
    url="http://www.uludag.org.tr/eng/pisi/",
    package_dir = {'': ''},
    packages = ['pisi', 'pisi.cli', 'pisi.actionsapi'],
    data_files = [ ('/usr/share/locale/tr/LC_MESSAGES', ['po/tr/pisi.mo'])], 
    scripts = ['pisi-cli'],
    cmdclass = {
        'install' : InstallPisi
    }
    )
