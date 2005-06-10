#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnuconfig import *
from libtoolize import *
from autotools import *
import pisiconfig

if __name__ == "__main__":
	os.chdir( pisiconfig.build_dir + 'popt-1.7' )
	gnuconfig_update()
	libtoolize()
	configure()
	make()
	install()
