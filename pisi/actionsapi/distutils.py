#!/usr/bin/python
# -*- coding: utf-8 -*-

# standard python modules
import os

# actions api modules
from actionglobals import glb
from pisi.ui import ui


def compile(parameters = ''):
    compile_string = ("/usr/bin/python2.3 setup.py build %s") % parameters
    os.system(compile_string)

def install(parameters = ''):
    dirs = glb.env
    
    dir_suffix = os.path.dirname(dirs.work_dir) + \
        glb.const.install_dir_suffix
        
    install_string = ("/usr/bin/python2.3 setup.py install --root=%s --no-compile %s") % (dir_suffix, parameters)
    os.system(install_string)

def optimize(parameters = ''):
    ui.info("Byte compiling python modules for python\n")

    dirs = glb.env

    dir_suffix = os.path.dirname(dirs.work_dir) + \
        glb.const.install_dir_suffix

    optimize_string = ("/usr/bin/python2.3 /usr/lib/python2.3/compileall.py -q %s") % dir_suffix + '/' + parameters
    os.system(optimize_string)
    optimize_string = ("/usr/bin/python2.3 -O /usr/lib/python2.3/compileall.py -q %s") % dir_suffix + '/' + parameters
    os.system(optimize_string)
