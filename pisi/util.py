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

def check_file(file, mode = os.F_OK):
    "shorthand to check if a file exists"
    if not os.access(file, mode):
        raise FileError("File " + file + " not found")

def check_dir(dir):
    """check if directory exists, and create if it doesn't.
    works recursively"""
    dir = dir.strip().rstrip("/")
    if not os.access(dir, os.F_OK):
        os.makedirs(dir)

def clean_dir(top):
    "Remove all content of a directory (top)"
    for root, dirs, files in os.walk(top, topdown=False):
	for name in files:
	    os.remove(os.path.join(root, name))
	for name in dirs:
	    os.rmdir(os.path.join(root, name))


def dir_size(dir):
    """ calculate the size of files under a dir
    based on the os module example"""
    getsize = os.path.getsize
    join = os.path.join
    def sizes():
        for root, dirs, files in os.walk(dir):
	    print sum([getsize(join(root, name)) for name in files])
            yield sum([getsize(join(root, name)) for name in files])
    return sum( sizes() )

def copy_file(src,dest):
    """copy source file to destination file"""
    check_file(src)
    check_dir(os.path.dirname(dest))
    fs = file(src, 'rb')
    fd = file(dest, 'wb')
    for l in fs:
        fd.write(l)

def copy_dir(src, dest):
    """copy source dir to destination dir recursively"""
    raise UtilError("not implemented")

def md5_file(filename):
    """calculate md5 hash of filename"""
    m = md5.new()
    f = file(filename, 'rb')
    for l in f:
        m.update(l)
    return m.hexdigest()

def run_batch(cmd):
    """run command non-interactively and report return value and output"""
    ui.info('running ' + cmd)
    a = os.popen(cmd)
    lines = a.readlines()
    ret = a.close()
    ui.debug('return value ' + ret)
    successful = ret == None
    if not successful:
      ui.error('ERROR: executing command: ' + cmd + '\n' + strlist(lines))
    return (successful,lines)

def strlist(l):
    """concatenate string reps of l's elements"""
    return string.join(map(lambda x: str(x) + ' ', l))
