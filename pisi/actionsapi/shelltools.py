#!/usr/bin/python
#-*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# Standart Python Modules
import os
import glob
import shutil

# Pisi Modules
from pisi.ui import ui

# ActionsAPI Modules
import pisi.actionsapi
import pisi.actionsapi.get

def can_access_file(sourceFile):
    '''test the existence of file'''
    return os.access(sourceFile, os.F_OK)

def can_access_directory(destinationDirectory):
    '''test readability, writability and executablility of directory'''
    return os.access(destinationDirectory, os.R_OK | os.W_OK | os.X_OK)

def makedirs(destinationDirectory):
    '''recursive directory creation function'''
    try:
        os.makedirs(destinationDirectory)
    except OSError:
        pass

def chmod(sourceFile, mode = 0755):
    '''change the mode of sourceFile to the mode'''
    for file in glob.glob(sourceFile):
        os.chmod(file, mode)
            
def unlink(sourceFile):
    os.unlink(sourceFile)

def unlinkDir(sourceDirectory):
    if can_access_directory(sourceDirectory):
        shutil.rmtree(sourceDirectory)
    else:
        ui.error('unlinkDir: remove failed...')

def move(sourceFile, destinationFile):
    '''recursively move a sourceFile or directory to destinationFile'''
    for file in glob.glob(sourceFile):
        shutil.move(file, destinationFile)

def copy(sourceFile, destinationFile):
    '''recursively copy a sourceFile or directory to destinationFile'''
    for file in glob.glob(sourceFile):
        shutil.copy(file, destinationFile)

def copytree(source, destination, sym=False):
    shutil.copytree(source, destination, sym)

def touch(sourceFile):
    '''changes the access time of the 'sourceFile', or creates it if it is not exist'''
    if glob.glob(sourceFile):
        for file in glob.glob(sourceFile):
            os.utime(file, None)
    else:
        f = open(sourceFile, 'w')
        f.close()

def cd(directoryName = ''):
    '''change directory'''
    current = os.getcwd()
    if directoryName:
        os.chdir(directoryName)
    else:
        os.chdir(os.path.dirname(current))

def ls(source):
    '''listdir'''
    if os.path.isdir(source):
        return os.listdir(source)
    else:
        return glob.glob(source)

def export(key, value):
    os.environ[key] = value

def system(command):
    ui.debug('executing %s\n' % command)
    p = os.popen(command)
    while 1:
        line = p.readline()
        if not line:
            break
        ui.debug(line)

    return p.close()

def isLink(sourceFile):
    return os.path.islink(sourceFile)

def realPath(sourceFile):
    return os.path.realpath(sourceFile)

def baseName(sourceFile):
    return os.path.basename(sourceFile)

def dirName(sourceFile):
    return os.path.dirname(sourceFile)

def sym(sourceFile, destinationFile):
    os.symlink(sourceFile, destinationFile)

