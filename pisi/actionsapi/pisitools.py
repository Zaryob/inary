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

from utils import makedirs, unlink, chmod
from pisi.util import copy_file, clean_dir

# actions api modules
from actionglobals import glb

env = glb.env
dirs = glb.dirs

def insinto(directory, filename, fileas=''):
    
    makedirs(env.install_dir + directory)

    if not fileas:
        for file in glob.glob(filename):
            if os.access(file, os.F_OK):
                copy_file(file, env.install_dir +
                    directory + os.path.basename(file))

    #XXX: toparla burayi..
    else:
        if os.access(filename, os.F_OK):
            copy_file(filename, env.install_dir +
                    directory + fileas)

def dodoc(*documentList):

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

def newdoc(source, destination):

    srcTag = env.src_name + '-' \
        + env.src_version + '-' \
        + env.src_release
    
    makedirs(os.path.join(env.install_dir,
                                 dirs.doc,
                                 srcTag))

    if os.access(source, os.F_OK):
        copy_file(source, 
            os.path.join(env.install_dir, 
                                         dirs.doc,
                                         srcTag,
                                         destination))

def dosed(filename, searchPattern, replacePattern = ''):
    for line in fileinput.input(filename, inplace = 1):
            line = re.sub(searchPattern, replacePattern, line)
            sys.stdout.write(line)

def dosbin(filename, destination = glb.dirs.sbin):

    makedirs(os.path.join(env.install_dir, destination))

    if os.access(filename, os.F_OK):
        copy_file(filename,
                        os.path.join(env.install_dir,
                                     destination,
                                     os.path.basename(filename)))

def doman(*filenameList):

    for item in filenameList:
        for filename in glob.glob(item):
            man, postfix = filename.split('.')
            destDir = os.path.join(env.install_dir, dirs.man, "man" + postfix)
    
            makedirs(destDir)

            gzfile = gzip.GzipFile(filename + '.gz', 'w', 9)
            gzfile.writelines(file(filename).xreadlines())
            gzfile.close()

            if os.access(filename + '.gz', os.F_OK):
                copy_file(filename + '.gz',
                            os.path.join(destDir,
                                     os.path.basename(filename + '.gz')))

def domove(source, destination):
    
    makedirs(env.install_dir + '/' + os.path.dirname(destination))
    try:
        shutil.move(env.install_dir + '/' + source, env.install_dir + '/' + destination)
    except OSError, e:
        pass
    
def dosym(source, destination):

    makedirs(env.install_dir + '/' + os.path.dirname(destination))
    
    if not os.path.islink(env.install_dir + destination):
        os.symlink(source, env.install_dir + destination)

def dolib(filename, destination = '/lib', srcDir = ''):

    if not srcDir:
        libFile = os.path.join(env.work_dir, env.src_name + "-" + env.src_version, filename)
    else:
        libFile = os.path.join(env.work_dir, srcDir, filename)

    makedirs(env.install_dir + destination)

    if os.access(libFile, os.F_OK):
        copy_file(libFile, env.install_dir + destination + '/' + filename)

def dodir(parameters = ''):

    makedirs(env.install_dir + parameters)

def newman(source, destination, srcDir = ''):

    man, postfix = destination.split('.')
    destDir = os.path.join(env.install_dir, dirs.man, "man" + postfix)

    makedirs(destDir)

    if not srcDir:
        file = os.path.join(env.work_dir, env.src_name + "-" + env.src_version, source)
    else:
        file = os.path.join(env.work_dir, srcDir, source)

    if os.access(file, os.F_OK):
                copy_file(file, os.path.join(destDir, os.path.basename(destination)))

def remove(filename):

    unlink(env.install_dir + filename)

def removeDir(dirname):
    
    clean_dir(env.install_dir + dirname)

def doecho(content, filename):
    makedirs(env.install_dir + '/' + os.path.dirname(filename))
    
    f = open(env.install_dir + '/' + filename, 'w')
    f.write(content)
    f.close()

def gen_usr_ldscript(parameters = ''): 

    dodir("/usr/lib")

    f = open(env.install_dir + '/usr/lib/' + parameters, 'w')
    content = '''
/* GNU ld script
    Since Pardus has critical dynamic libraries
    in /lib, and the static versions in /usr/lib,
    we need to have a "fake" dynamic lib in /usr/lib,
    otherwise we run into linking problems.
*/
GROUP ( /lib/%s )
''' % parameters
    f.write(content)
    f.close()
    chmod(env.install_dir + "/usr/lib/%s" % parameters)

def preplib(parameters = ''):
    os.system("/sbin/ldconfig -n -N %s%s" % (env.install_dir, parameters))
