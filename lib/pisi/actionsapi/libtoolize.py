#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

def libtoolize():
    ''' FIXME: Düzgün hale getirilecek '''
    ''' patch source with ltmain patches '''

    # This is wrong! Action files should only operate on the build
    # directory. And shouldn't depend on external files. If a patch is
    # need to be applied it is PisiBuild's job to do it!
    os.system('patch -sN < ' + Context.lib_dir() + '/portage-1.4.1.patch')
    os.system('patch -sN < ' + Context.lib_dir() + '/sed-1.4.0.patch')
