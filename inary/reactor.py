# -*- coding: utf-8 -*-
#
#Copyright (C) 2019, Ali Rıza KESKİN (sulincix)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary.context as ctx
import inary.db
import inary.util as util
import os
import sys

def post_install(package_name, provided_scripts,
             scriptpath, metapath, filepath,
             fromVersion, fromRelease, toVersion, toRelease):
    """Do package's post install operations"""
    pkg_path = metapath.replace("metadata.xml","scom")
    if(os.path.isfile(pkg_path+"/package.py")):
        i=os.system('cd {} ; python3 -c \'import package\nif(hasattr(package,"postInstall")):\n package.postInstall("{}",{},"{}",{})\''.format((pkg_path),fromVersion, fromRelease, toVersion, toRelease))
        if(i!=0):
            raise SystemExit
    elif(os.path.isfile(pkg_path+"/package.sh")):
        i=os.system('source {}/package.sh ; postInstall "{}" {} "{}" {}'.format((pkg_path),fromVersion, fromRelease, toVersion, toRelease))
        if(i!=0):
            raise SystemExit
    else:
        return 0

def pre_install(package_name, provided_scripts,
             scriptpath, metapath, filepath,
             fromVersion, fromRelease, toVersion, toRelease):
    """Do package's pre install operations"""
    pkg_path = metapath.replace("metadata.xml","scom")
    if(os.path.isfile(pkg_path+"/package.py")):
        i=os.system('cd {} ; python3 -c \'import package\nif(hasattr(package,"preInstall")):\n  package.preInstall("{}",{},"{}",{})\''.format((pkg_path),fromVersion, fromRelease, toVersion, toRelease))
        if(i!=0):
            raise SystemExit
    elif(os.path.isfile(pkg_path+"/package.sh")):
        i=os.system('source {}/package.sh ; preInstall "{}" "{}" "{}" "{}"'.format((pkg_path),fromVersion, fromRelease, toVersion, toRelease))
        if(i!=0):
            raise SystemExit
    else:
        return 0
    

def post_remove(package_name, metapath, filepath, provided_scripts=None):
    """Do package's post removal operations"""
    pkg_path = metapath.replace("metadata.xml","scom")
    if(os.path.isfile(pkg_path+"/package.py")):
        i=os.system('cd {} ; python3 -c \'import package\nif(hasattr(package,"postRemove")):\n package.postRemove()\''.format(pkg_path))
        if(i!=0):
            raise SystemExit
    elif(os.path.isfile(pkg_path+"/package.sh")):
        i=os.system('source {}/package.sh ; postRemove '.format((pkg_path)))
        if(i!=0):
            raise SystemExit
    else:
        return 0
   

def pre_remove(package_name, metapath, filepath,provided_scripts=None):
    """Do package's post removal operations"""
    pkg_path = metapath.replace("metadata.xml","scom")
    if(os.path.isfile(pkg_path+"/package.py")):
        i=os.system('cd {} ; python3 -c \'import package\nif(hasattr(package,"preRemove")):\n package.preRemove()\''.format(pkg_path))
        if(i!=0):
            raise SystemExit
    elif(os.path.isfile(pkg_path+"/package.sh")):
        i=os.system('source {}/package.sh ; preRemove'.format((pkg_path)))
        if(i!=0):
            raise SystemExit
    else:
        return 0
