#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from pisi.context import const

# Global variables for compiling KDE programs...
kde_dir = os.getenv('KDEDIR')
qt_dir = os.getenv('QTDIR')
qt_libdir = os.getenv('QTDIR') + '/lib/'

def configure(parameters = ''):
    ''' FIXME: Düzgün hale getirilecek '''
    ''' parameters = '--with-nls --with-libusb --with-something-usefull '''

    configure_string = './configure --prefix=%s \
                --host=i686-pc-linux-gnu \
                --with-x \
                --enable-mitshm \
                --with-qt-dir=%s \
                --enable-mt \
                --with-qt-libraries=%s \
                %s' % (kde_dir, qt_dir, qt_libdir, parameters)

    os.system(configure_string)

def make():
    ''' FIXME: Düzgün hale getirilecek '''
    os.system('make')

def install():
    ''' FIXME: Düzgün hale getirilecek '''
    ''' dir_suffix = /var/tmp/pisi/ _paket_adı_ /image/ '''
    global const

    dir_suffix = os.path.dirname(os.path.dirname(os.getcwd())) + \
        const.install_dir_suffix
    
    install_string = 'make prefix=%s/%s install' % (dir_suffix, kde_dir)
    os.system(install_string)
