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

# Standart Python Modules
import os
import glob
import shutil

# Pisi Modules
import pisi.context as ctx

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

def echo(destionationFile, content):
    try:
        f = open(destionationFile, 'a')
        f.write("%s\n" % content)
        f.close()
    except IOError:
        ctx.ui.error('\n!!! ActionsAPI [echo]: Can\'t append to file...\n')

def chmod(sourceFile, mode = 0755):
    '''change the mode of sourceFile to the mode'''
    for file in glob.glob(sourceFile):
        if can_access_file(file):
            try:
                os.chmod(file, mode)
            except OSError:
                ctx.ui.error('\n!!! ActionsAPI [chmod]: Operation not permitted...\n')
        else:
            ctx.ui.error('\n!!! ActionsAPI [chmod]: File doesn\'t exists...\n')

def chown(sourceFile, uid = 0, gid = 0):
    '''change the owner and group id of sourceFile to the numeric uid and gid'''
    if can_access_file(sourceFile):
        try:
            os.chown(sourceFile, uid, gid)
        except OSError:
            ctx.ui.error('\n!!! ActionsAPI [chown]: Operation not permitted...\n')
    else:
        ctx.ui.error('\n!!! ActionsAPI [chown]: File doesn\'t exists...\n')

def sym(sourceFile, destinationFile):
    '''creates symbolic link'''
    try:
        os.symlink(sourceFile, destinationFile)
    except OSError:
        ctx.ui.error('\n!!! ActionsAPI [sym]: Permission denied...\n')

def unlink(sourceFile):
    '''remove the file path'''
    if isFile(sourceFile) or isLink(sourceFile):
        try:
            os.unlink(sourceFile)
        except OSError:
            ctx.ui.error('\n!!! ActionsAPI [unlink]: Permission denied...\n')
    elif isDirectory(sourceFile):
        pass
    else:
        ctx.ui.error('\n!!! ActionsAPI [unlink]: File doesn\'t exists...\n')

def unlinkDir(sourceDirectory):
    '''delete an entire directory tree'''
    if isDirectory(sourceDirectory) or isLink(sourceDirectory):
        try:
            shutil.rmtree(sourceDirectory)
        except OSError:
            ctx.ui.error('\n!!! ActionsAPI [unlinkDir]: Operation not permitted...\n')
    elif isFile(sourceDirectory):
        pass                                
    else:
        ctx.ui.error('\n!!! ActionsAPI [unlinkDir]: Directory doesn\'t exists...\n')

def move(sourceFile, destinationFile):
    '''recursively move a sourceFile or directory to destinationFile'''
    for file in glob.glob(sourceFile):
        if isFile(file) or isLink(file) or isDirectory(file):
            try:
                shutil.move(file, destinationFile)
            except OSError:
                ctx.ui.error('\n!!! ActionsAPI [move]: Permission denied...\n')
        else:
            ctx.ui.error('\n!!! ActionsAPI [move]: File doesn\'t exists...\n')

def copy(sourceFile, destinationFile):
    '''recursively copy a sourceFile or directory to destinationFile'''
    for file in glob.glob(sourceFile):
        if isFile(file) or isLink(file):
            try:
                shutil.copy(file, destinationFile)
            except IOError:
                ctx.ui.error('\n!!! ActionsAPI [copy]: Permission denied...\n')
        else:
            ctx.ui.error('\n!!! ActionsAPI [copy]: File doesn\'t exists...\n')

def copytree(source, destination, sym = False):
    '''recursively copy an entire directory tree rooted at source'''
    if isDirectory(file) or isLink(file):
        try:
            shutil.copytree(source, destination, sym)
        except OSError:
            ctx.ui.error('\n!!! ActionsAPI [copytree]: Permission denied...\n')
    else:
        ctx.ui.error('\n!!! ActionsAPI [copytree]: Directory doesn\'t exists...\n')

def touch(sourceFile):
    '''changes the access time of the 'sourceFile', or creates it if it is not exist'''
    if glob.glob(sourceFile):
        for file in glob.glob(sourceFile):
            os.utime(file, None)
    else:
        try:
            f = open(sourceFile, 'w')
            f.close()
        except IOError:
            ctx.ui.error('\n!!! ActionsAPI [touch]: Permission denied...\n')

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
    '''export environ variable'''
    os.environ[key] = value

def isLink(sourceFile):
    '''return True if sourceFile refers to a symbolic link'''
    return os.path.islink(sourceFile)

def isFile(sourceFile):
    '''return True if sourceFile is an existing regular file'''
    return os.path.isfile(sourceFile)

def isDirectory(sourceDirectory):
    '''Return True if sourceFile is an existing directory'''
    return os.path.isdir(sourceDirectory)

def realPath(sourceFile):
    '''return the canonical path of the specified filename, eliminating any symbolic links encountered in the path'''
    return os.path.realpath(sourceFile)

def baseName(sourceFile):
    '''return the base name of pathname sourceFile'''
    return os.path.basename(sourceFile)

def dirName(sourceFile):
    '''return the directory name of pathname path'''
    return os.path.dirname(sourceFile)

def system(command):
    #FIXME: String formatting
    command = command.replace("                 ", " ")
    ctx.ui.debug('executing %s\n' % command)
    p = os.popen(command)
    while 1:
        line = p.readline()
        if not line:
            break
        ctx.ui.debug(line)

    return p.close()
