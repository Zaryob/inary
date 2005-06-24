#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, shutil

def dodoc(*documentList):
    install_dir = os.getenv('INSTALL_DIR')
    src_name = os.getenv('SRC_NAME')
    src_version = os.getenv('SRC_VERSION')
    src_release = os.getenv('SRC_RELEASE')

    srcTag = src_name + '-' + src_version + '-' + src_release
    
    # FIXME: Exception yiyoruz eğer klasör mevcutsa, adam edilecek!
    os.makedirs(install_dir + '/' + 'usr/share/doc/' + srcTag)
  
    for document in documentList:
        if os.access(document, os.F_OK):
            shutil.copyfile(document, os.path.join(install_dir, \
                'usr/share/doc/' + srcTag + '/' + os.path.basename(document)))
                