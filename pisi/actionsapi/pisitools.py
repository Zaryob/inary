#!/usr/bin/python
# -*- coding: utf-8 -*-

# standard python modules
import os
import gzip
import shutil
import fileinput
import re
import sys
import glob

from utils import makedirs, unlink
from pisi.util import copy_file, clean_dir

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

    for item in documentList:
        for document in glob.glob(item):
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
    try:
        shutil.move(env.install_dir + '/' + source, env.install_dir + '/' + destination)
    except OSError, e:
        pass
    
def dosym(source, destination):
    env = glb.env

    makedirs(env.install_dir + '/' + os.path.dirname(destination))
    
    if not os.path.islink(env.install_dir + destination):
        os.symlink(source, env.install_dir + destination)

def dolib(filename, destination = '/lib', srcDir = ''):
    env = glb.env

    if not srcDir:
        libFile = os.path.join(env.work_dir, env.src_name + "-" + env.src_version, filename)
    else:
        libFile = os.path.join(env.work_dir, srcDir, filename)

    makedirs(env.install_dir + destination)

    if os.access(libFile, os.F_OK):
        copy_file(libFile, env.install_dir + destination + '/' + filename)

def dodir(parameters = ''):
    env = glb.env

    makedirs(env.install_dir + parameters)

def remove(filename):
    env = glb.env
    
    unlink(env.install_dir + filename)

def removeDir(dirname):
    env = glb.env
    
    clean_dir(env.install_dir + dirname)
