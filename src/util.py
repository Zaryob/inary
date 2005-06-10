# -*- coding: utf-8 -*-
# misc. utility functions, including process and file utils

import os
import sys
import string

def information(message):
    sys.stdout.write(message)
    sys.stdout.flush()

# check if directory exists, and create if it doesn't
# works recursively
# FIXME: could hav a better name
def check_dir(dir):
    dir = dir.rstrip()
    dir = dir.rstrip("/")
    #print 'check dir ', dir
    if not os.access(dir, os.F_OK):
        # does the parent exist?
        (parent_dir, curr_dir) = os.path.split(dir)
        check_dir(parent_dir)
        os.mkdir(dir)

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

class ArgError(Exception):
    pass

def usage(progname = "pisi-build"):
    print """
Usage:
%s [options] package-name.pspec
""" %(progname)
