#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,sys

sys.path.append('..')
import config

def libtoolize():
        ''' FIXME: Düzgün hale getirilecek '''
	''' patch source with ltmain patches '''

	os.system( 'patch -sN < ' + config.lib_dir() + '/portage-1.4.1.patch' )
	os.system( 'patch -sN < ' + config.lib_dir() + '/sed-1.4.0.patch' )
