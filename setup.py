#!/usr/bin/env python
#
# Install script for tengis.
#

from distutils.core import setup

setup(name="tengis",
      version="0.1",
      description="Pardus Package Manager",
      long_description="blah blah blah",
      license="GNU GPL",
      author="Pardus Developers",
      author_email="pardus@uludag.org.tr",
      url="http://uludag.org.tr",
      package_dir = {'': 'lib'},
      packages = ['pisi'],
      scripts = ['bin/pisi-build', 'bin/pisi-install']
     )
