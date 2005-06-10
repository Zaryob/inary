#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnuconfig import *
from libtoolize import *
from autotools import *

sys.path.append('..')
import pisiconfig

if __name__ == "__main__":
	package_name = 'popt-1.7'

	os.chdir( pisiconfig.tmp_dir + package_name + '/build' )

	gnuconfig_update( package_name )
	libtoolize()
	configure( '--with-nls' )
	make()
	install()
