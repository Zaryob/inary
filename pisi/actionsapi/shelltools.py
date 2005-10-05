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
import pwd

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

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
        ctx.ui.error(_(' ActionsAPI [echo]: Can\'t append to file %s...') % (destionationFile))

def chmod(sourceFile, mode = 0755):
    '''change the mode of sourceFile to the mode'''
    for file in glob.glob(sourceFile):
        if can_access_file(file):
            try:
                os.chmod(file, mode)
            except OSError:
                ctx.ui.error(_(' ActionsAPI [chmod]: Operation not permitted: %s (mode: %s)') \
                                                                % (file, mode))
        else:
            ctx.ui.error(_(' ActionsAPI [chmod]: File %s doesn\'t exists.') % (file))

def chown(sourceFile, uid = "root", gid = "root"):
    '''change the owner and group id of sourceFile to uid and gid'''
    if can_access_file(sourceFile):
        try:
            os.chown(sourceFile, pwd.getpwnam(uid)[2], pwd.getpwnam(gid)[3])
        except OSError:
            ctx.ui.error(_(' ActionsAPI [chown]: Operation not permitted: %s (uid: %s, gid: %s)') \
                                                 % (sourceFile, uid, gid))
    else:
        ctx.ui.error(_(' ActionsAPI [chown]: File %s doesn\'t exists.') % sourceFile)

def sym(sourceFile, destinationFile):
    '''creates symbolic link'''
    try:
        os.symlink(sourceFile, destinationFile)
    except OSError:
        ctx.ui.error(_(' ActionsAPI [sym]: Permission denied: %s to %s') % (file, destinationFile))

def unlink(sourceFile):
    '''remove the file path'''
    if isFile(sourceFile) or isLink(sourceFile):
        try:
            os.unlink(sourceFile)
        except OSError:
            ctx.ui.error(_(' ActionsAPI [unlink]: Permission denied: %s.') % (sourceFile))
    elif isDirectory(sourceFile):
        pass
    else:
        ctx.ui.error(_(' ActionsAPI [unlink]: File %s doesn\'t exists.') % (sourceFile))

def unlinkDir(sourceDirectory):
    '''delete an entire directory tree'''
    if isDirectory(sourceDirectory) or isLink(sourceDirectory):
        try:
            shutil.rmtree(sourceDirectory)
        except OSError:
            ctx.ui.error(_(' ActionsAPI [unlinkDir]: Operation not permitted: %s') % (sourceDirectory))
    elif isFile(sourceDirectory):
        pass                                
    else:
        ctx.ui.error(_(' ActionsAPI [unlinkDir]: Directory %s doesn\'t exists.') % (sourceDirectory))

def move(sourceFile, destinationFile):
    '''recursively move a sourceFile or directory to destinationFile'''
    for file in glob.glob(sourceFile):
        if isFile(file) or isLink(file) or isDirectory(file):
            try:
                shutil.move(file, destinationFile)
            except OSError:
                ctx.ui.error(_(' ActionsAPI [move]: Permission denied: %s to %s') % (file, destinationFile))
        else:
            ctx.ui.error(_(' ActionsAPI [move]: File %s doesn\'t exists.') % (file))

def copy(sourceFile, destinationFile):
    '''recursively copy a sourceFile or directory to destinationFile'''
    for file in glob.glob(sourceFile):
        if isFile(file) or isLink(file):
            try:
                shutil.copy(file, destinationFile)
            except IOError:
                ctx.ui.error(_('ActionsAPI [copy]: Permission denied: %s to %s') % (file, destinationFile))
        elif isDirectory(file):
            copytree(file, destinationFile)
        else:
            ctx.ui.error(_('ActionsAPI [copy]: File %s does not exist.') % file)

def copytree(source, destination, sym = False):
    '''recursively copy an entire directory tree rooted at source'''
    if isDirectory(source) or isLink(source):
        try:
            shutil.copytree(source, destination, sym)
        except OSError:
            ctx.ui.error(_(' ActionsAPI [copytree]: Permission denied: %s to %s') % (source, destination))
    else:
        ctx.ui.error(_(' ActionsAPI [copytree]: Directory %s doesn\'t exists.') % (source))

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
            ctx.ui.error(_(' ActionsAPI [touch]: Permission denied: %s') % (sourceFile))

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
    ctx.ui.debug(_('executing %s') % command)
    p = os.popen(command)
    while 1:
        line = p.readline()
        if not line:
            break
        ctx.ui.debug(line[0:len(line)-1])

    return p.close()
