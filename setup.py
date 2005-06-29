#!/usr/bin/env python
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
