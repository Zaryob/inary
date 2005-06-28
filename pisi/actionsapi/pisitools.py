#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, shutil
import gzip

def dodoc(*documentList):

    install_dir = os.getenv('INSTALL_DIR')
    src_name = os.getenv('SRC_NAME')
    src_version = os.getenv('SRC_VERSION')
    src_release = os.getenv('SRC_RELEASE')

    srcTag = src_name + '-' + src_version + '-' + src_release
    
    try:
        os.makedirs(install_dir + '/' + 'usr/share/doc/' + srcTag)
    except OSError:
        pass

    for document in documentList:
        if os.access(document, os.F_OK):
            shutil.copyfile(document, os.path.join(install_dir, \
                'usr/share/doc/' + srcTag + '/' + os.path.basename(document)))

def dosed(filename, *sedPattern):
    #FIXME: Convert to python
    for pattern in sedPattern:
        os.system('sed -i -e \'' + pattern + '\' ' +  filename)

def dosbin(filename, destination='/usr/sbin'):
    install_dir = os.getenv('INSTALL_DIR')

    try:
        os.makedirs(install_dir + destination)
    except OSError:
        pass

    if os.access(filename, os.F_OK):
        shutil.copyfile(filename, install_dir + destination + '/' \
                        + os.path.basename(filename))

def doman(filename):
    install_dir = os.getenv('INSTALL_DIR')
    
    man, postfix = filename.split('.')

    try:
        os.makedirs(install_dir + '/usr/share/man/man' + postfix)
    except OSError:
        pass

    gzfile = gzip.GzipFile(filename + '.gz', 'w', 9)
    gzfile.writelines(file(filename).xreadlines())
    gzfile.close()

    if os.access(filename, os.F_OK):
        shutil.copyfile(filename + '.gz', install_dir + '/usr/share/man/man' \
                        + postfix  + '/' + os.path.basename(filename))

