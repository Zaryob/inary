# -*- coding: utf-8 -*-
#
# Copyright (C) 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

"""Basic shell utilities working on files and directories."""

import os
import shutil
import subprocess


###############################
# Directory related functions #
###############################

def remove_dir(path):
    """Remove all content of a directory."""
    if os.path.exists(path):
        shutil.rmtree(path)


def dir_size(dir):
    """Calculate the size of files under a directory."""
    from os.path import getsize, islink, isdir, exists, join

    if exists(dir) and (not isdir(dir) and not islink(dir)):
        #so, this is not a directory but file..
        return getsize(dir)

    if islink(dir):
        return int(len(os.readlink(dir)))

    def sizes():
        for root, dirs, files in os.walk(dir):
            yield sum([getsize(join(root, name)) for name in files if not islink(join(root,name))])
            yield sum([int(len(os.readlink((join(root, name))))) for name in files if islink(join(root,name))])
    return sum( sizes() )



#########################
# File related funtions #
#########################

def touch(filename):
    """Update file modification date, create file if necessary"""
    try:
        if os.path.exists(filename):
            os.utime(filename, None)
        else:
            open(filename, "w").close()
    except IOError as e:
        if e.errno != 13:
            raise
        else:
            return False
    except OSError as e:
        if e.errno != 13:
            raise
        else:
            return False
    return True

########################
#    Process tools     #
########################

def capture(*cmd):
    """Capture output of the command without running a shell"""
    a = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return a.communicate()

def run(*cmd):
    """Run a command without running a shell, only output errors"""
    f = open("/dev/null", "w")
    return subprocess.call(cmd, stdout=f)

def run_full(*cmd):
    """Run a command without running a shell, with full output"""
    return subprocess.call(cmd)

def run_quiet(*cmd):
    """Run the command without running a shell and no output"""
    f = file("/dev/null", "w")
    return subprocess.call(cmd, stdout=f, stderr=f)

