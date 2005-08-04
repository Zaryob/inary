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

# ActionsAPI Modules
import get

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
        print "unlinkDir: remove failed..."

def move(sourceFile, destinationFile):
    '''recursively move a sourceFile or directory to destinationFile'''
    shutil.move(sourceFile, destinationFile)

def copy(sourceFile, destinationFile):
    '''recursively copy a sourceFile or directory to destinationFile'''
    shutil.copy(sourceFile, destinationFile)

def touch(sourceFile):
    for file in glob.glob(sourceFile):
        os.utime(file, None)

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
        
