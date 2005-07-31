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

# Generic functions for common usage of pisitools #

# Standart Python Modules
import os
import glob

# ActionsAPI Modules
from shelltools import *

class FileError(Exception):
    pass

class ArgumentError(Exception):
    pass

def executable_insinto(sourceFile, destinationDirectory):
    '''insert a executable file into destinationDirectory'''

    if not sourceFile or not destinationDirectory:
        raise ArgumentError("Insufficient arguments...")

    if not can_access_file(sourceFile):
        raise FileError("File doesn't exists or permission denied...")

    if can_access_directory(destinationDirectory) and os.path.isdir(destinationDirectory):
        os.system("install -m0755 -o root -g root %s %s" % (sourceFile, destinationDirectory))
    else:
        makedirs(destinationDirectory)
        os.system("install -m0755 -o root -g root %s %s" % (sourceFile, destinationDirectory))

def readable_insinto(destinationDirectory, *sourceFiles):
    '''inserts file list into destinationDirectory'''

    if not sourceFiles or not destinationDirectory:
        raise ArgumentError("Insufficient arguments...")

    if not can_access_directory(destinationDirectory):
        makedirs(destinationDirectory)

    for sourceFile in sourceFiles:
        for source in glob.glob(sourceFile):
            os.system("install -m0644 %s %s" % (source, destinationDirectory))
