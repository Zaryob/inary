#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnuconfig import *
from libtoolize import *
from autotools import *

sys.path.append('..')
import config


if __name__ == "__main__":
	''' WILLBE: Unpack module will pass the package name to action script '''
	package_name = 'popt-1.7'
	''' WILLBE: pisi-build call action script after entered the build directory '''
	os.chdir( config.tmp_dir + '/' + package_name + '/build' )

	gnuconfig_update()
	libtoolize()
	configure( '--with-nls' )
	make()
	install()
