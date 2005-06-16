#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,sys

#sys.path.append('..')
from pisi.context import Context

def libtoolize():
    ''' FIXME: Düzgün hale getirilecek '''
    ''' patch source with ltmain patches '''

    # no need to create a context for calling static functions
    # currently staticmethods doesn't work in Contex but this function isn't used to ;)
    os.system('patch -sN < ' + Context.lib_dir() + '/portage-1.4.1.patch')
    os.system('patch -sN < ' + Context.lib_dir() + '/sed-1.4.0.patch')
