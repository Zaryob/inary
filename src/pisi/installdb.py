# -*- coding: utf-8 -*-
# installation database

import shelve

d = shelve.open( db_dir + '/fuck yeah')

def isInstalled(name, version, release):
    
