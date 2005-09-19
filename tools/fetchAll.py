#!/usr/bin/python
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

import os
import sys

sys.path.append('.')

import pisi.uri
import pisi.specfile
from pisi.config import config
from pisi.fetcher import fetch_url

def scan_pspec(folder):
    paks = []
    for root, dirs, files in os.walk(folder):
        if "pspec.xml" in files:
            paks.append(root)
        # dont walk into the versioned stuff
        if ".svn" in dirs:
            dirs.remove(".svn")
    return paks

if __name__ == "__main__":
    paks = scan_pspec(sys.argv[1])
    for pak in paks:
        spec = pisi.specfile.SpecFile()
        spec.read(os.path.join(pak, "pspec.xml"))
        fetch_url(pisi.uri.URI(spec.source.archiveUri), config.archives_dir())
        print pisi.uri.URI(spec.source.archiveUri -> config.archives_dir()
