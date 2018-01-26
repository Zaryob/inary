#-*- coding: utf-8 -*-
#
# Copyright (C) 2016 - 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

# Generic functions for common usage of inarytools #

# Standart Python Modules
import os
import glob

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

# Inary Modules
import inary.context as ctx

# ActionsAPI Modules
import inary.actionsapi
from inary.actionsapi.shelltools import *

class FileError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)

class ArgumentError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)

def executable_insinto(destinationDirectory, *sourceFiles):
    '''insert a executable file into destinationDirectory'''

    if not sourceFiles or not destinationDirectory:
        raise ArgumentError(_('Insufficient arguments.'))

    if not can_access_directory(destinationDirectory):
        makedirs(destinationDirectory)

    for sourceFile in sourceFiles:
        sourceFileGlob = glob.glob(sourceFile)
        if len(sourceFileGlob) == 0:
            raise FileError(_("No executable file matched pattern \"{}\".").format(sourceFile))

        for source in sourceFileGlob:
            # FIXME: use an internal install routine for these
            system('install -m0755 -o root -g root {0} {1}'.format(source, destinationDirectory))

def readable_insinto(destinationDirectory, *sourceFiles):
    '''inserts file list into destinationDirectory'''

    if not sourceFiles or not destinationDirectory:
        raise ArgumentError(_('Insufficient arguments.'))

    if not can_access_directory(destinationDirectory):
        makedirs(destinationDirectory)

    for sourceFile in sourceFiles:
        sourceFileGlob = glob.glob(sourceFile)
        if len(sourceFileGlob) == 0:
            raise FileError(_("No file matched pattern \"{}\".").format(sourceFile))

        for source in sourceFileGlob:
            system('install -m0644 "{0}" {1}'.format(source, destinationDirectory))

def lib_insinto(sourceFile, destinationDirectory, permission = 0o644):
    '''inserts a library fileinto destinationDirectory with given permission'''

    if not sourceFile or not destinationDirectory:
        raise ArgumentError(_('Insufficient arguments.'))

    if not can_access_directory(destinationDirectory):
        makedirs(destinationDirectory)

    if os.path.islink(sourceFile):
        os.symlink(os.path.realpath(sourceFile), os.path.join(destinationDirectory, sourceFile))
    else:
        system('install -m0%o %s %s' % (permission, sourceFile, destinationDirectory))
