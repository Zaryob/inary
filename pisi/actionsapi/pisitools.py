#!/usr/bin/python
# -*- coding: utf-8 -*-

# standard python modules
import os
import gzip
import shutil
import fileinput
import re
import sys

from utils import makedirs
from pisi.util import copy_file

# actions api modules
from actionglobals import glb

def dodoc(*documentList):
    env = glb.env
    dirs = glb.dirs

    srcTag = env.src_name + '-' \
        + env.src_version + '-' \
        + env.src_release
    
    makedirs(os.path.join(env.install_dir,
                                 dirs.doc,
                                 srcTag))

    for document in documentList:
        if os.access(document, os.F_OK):
            copy_file(document, 
                            os.path.join(env.install_dir,
                                         dirs.doc,
                                         srcTag,
                                         os.path.basename(document)))

def dosed(filename, searchPattern, replacePattern = ''):
    for line in fileinput.input(filename, inplace = 1):
            line = re.sub(searchPattern, replacePattern, line)
            sys.stdout.write(line)

def dosbin(filename, destination = glb.dirs.sbin):
    env = glb.env

    makedirs(os.path.join(env.install_dir, destination))

    if os.access(filename, os.F_OK):
        copy_file(filename,
                        os.path.join(env.install_dir,
                                     destination,
                                     os.path.basename(filename)))

def doman(*filenameList):
    env = glb.env
    dirs = glb.dirs

    for filename in filenameList:
        man, postfix = filename.split('.')
        destDir = os.path.join(env.install_dir, dirs.man, "man" + postfix)
    
        makedirs(destDir)

        gzfile = gzip.GzipFile(filename + '.gz', 'w', 9)
        gzfile.writelines(file(filename).xreadlines())
        gzfile.close()

        if os.access(filename, os.F_OK):
            copy_file(filename + '.gz',
                            os.path.join(destDir,
                                     os.path.basename(filename)))

def domove(source, destination):
    env = glb.env

    makedirs(env.install_dir + '/' + os.path.dirname(destination))
    shutil.move(env.install_dir + '/' + source, env.install_dir + '/' + destination)
    
def dosym(source, destination):
    env = glb.env

    makedirs( env.install_dir + '/' + os.path.dirname(destination))
    
    if not os.path.islink(env.install_dir + destination):
        os.symlink(source, env.install_dir + destination)
