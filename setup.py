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

from distutils.core import setup

setup(name="pisi",
      version="0.1",
      description="Pardus Package Manager",
      long_description="blah blah blah",
      license="GNU GPL",
      author="Pardus Developers",
      author_email="hotmail@uludag.org.tr",
      url="http://uludag.org.tr",
      package_dir = {'': ''},
      packages = ['pisi', 'pisi.cli', 'pisi.actionsapi'],
      package_data = {'pisi.actionsapi' : ['share/*'] }
      scripts = ['pisi-build', 'pisi-install']
     )
