#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

def libtoolize():
	os.system( 'patch -sN < /var/lib/pisi/portage-1.4.1.patch' )
	os.system( 'patch -sN < /var/lib/pisi/sed-1.4.0.patch' )
