# -*- coding: utf-8 -*-
# misc. utility functions, including process and file utils
# maintainer: eray and caglar and baris and meren!

import os
import sys
import md5
from ui import ui

class FileError(Exception):
    pass

class UtilError(Exception):
    pass

# shorthand to check if a file exists
def check_file(file, mode = os.F_OK):
    if not os.access(file, mode):
        raise FileError("File " + file + " not found")

# check if directory exists, and create if it doesn't
# works recursively
# FIXME: could have a better name
def check_dir(dir):
    dir = dir.strip().rstrip("/")
    if not os.access(dir, os.F_OK):
        os.makedirs(dir)

def clean_dir(top):
    """Remove all content of a directory (top)"""
    for root, dirs, files in os.walk(top, topdown=False):
	for name in files:
	    os.remove(os.path.join(root, name))
	for name in dirs:
	    os.rmdir(os.path.join(root, name))


# calculate the size of files under a dir
# based on the os module example
def dir_size(dir):
    from os.path import join, getsize
    def sizes():
        for root, dirs, files in os.walk(dir):
            print sum(getsize(join(root, name)) for name in files)
            yield sum(getsize(join(root, name)) for name in files)
    return sum( sizes() )

def copy_file(s,d):
    check_file(s)
    check_dir(os.path.dirname(d))
    fs = file(s, 'rb')
    fd = file(d, 'wb')
    for l in fs:
        fd.write(l)

def copy_dir():
    raise UtilError("not implemented")

def md5_file(filename):
    m = md5.new()
    f = file(filename, 'rb')
    for l in f:
        m.update(l)
    return m.hexdigest()

# run a command non-interactively
def run_batch(cmd):
    ui.info('running ' + cmd)
    a = os.popen(cmd)
    lines = a.readlines()
    ret = a.close()
    ui.debug('return value ' + ret)
    successful = ret == None
    if not successful:
      ui.error('ERROR: executing command: ' + cmd + '\n' + strlist(lines))
    return (successful,lines)

# print a list
def strlist(l):
    return string.join(map(lambda x: str(x) + ' ', l))
