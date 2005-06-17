# -*- coding: utf-8 -*-
# misc. utility functions, including process and file utils
# maintainer: eray and caglar and baris and meren!

import os
import sys
import md5

# check if directory exists, and create if it doesn't
# works recursively
# FIXME: could have a better name
def check_dir(dir):
    dir = dir.strip().rstrip("/")
    #print 'check dir ', dir
    if not os.access(dir, os.F_OK):
        # does the parent exist?
        (parent_dir, curr_dir) = os.path.split(dir)
        if parent_dir != "/":
            check_dir(parent_dir)
        try:
            os.mkdir(dir)
        except OSError, e:
            raise UtilError("%s" % e)

def purge_dir(top):
    """Remove all content of a directory (top)"""
    for root, dirs, files in os.walk(top, topdown=False):
	for name in files:
	    os.remove(os.path.join(root, name))
	for name in dirs:
	    os.rmdir(os.path.join(root, name))

# TODO:
def copy_file():
    pass

def remove_file():
    # unlink file
    pass

def copy_dir():
    pass

def md5_file(filename):
    m = md5.new()
    f = file(filename, 'rb')
    for l in f:
        m.update(l)
    return m.hexdigest()

# run a command non-interactively
def run_batch(cmd):
    print 'running ', cmd
    a = os.popen(cmd)
    lines = a.readlines()
    ret = a.close()
    print 'return value ', ret
    successful = ret == None
    if not successful:
      print 'ERROR: executing command', cmd
      for x in lines:
        print x
    return (successful,lines)

# print a list
def strlist(l):
    return string.join(map(lambda x: str(x) + ' ', l))

class UtilError(Exception):
    pass
