#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,sys
sys.path.append('..')
import config

global package_name 

if __name__ == "__main__":
    ''' WILLBE: Unpack module will pass the package name to action script '''
    package_name = 'popt-1.7'
    ''' WILLBE: pisi-build call action script after entered the build directory '''

    os.chdir( config.tmp_dir() + '/' + package_name + '/build' )
    
    locals = globals = {}
    exec compile( open( sys.argv[1] ).read(), "error", "exec" ) in locals,globals
    locals['src_setup']()
    locals['src_build']()
    locals['src_install']()
