#!/usr/bin/python
# -*- coding: utf-8 -*-

# standard python modules
import os

# actions api modules
from actionglobals import glb

# Global variables for compiling KDE programs...
kde_dir = os.getenv('KDEDIR')
qt_dir = os.getenv('QTDIR')
qt_libdir = os.path.join(os.getenv('QTDIR') + 'lib/')

def configure(parameters = ''):
    ''' FIXME: Düzgün hale getirilecek '''
    ''' parameters = '--with-nls --with-libusb --with-something-usefull '''

    configure_string = './configure --prefix=%s \
                --host=%s \
                --with-x \
                --enable-mitshm \
                --with-qt-dir=%s \
                --enable-mt \
                --with-qt-libraries=%s \
                %s' % (kde_dir, config.flags.host, qt_dir, qt_libdir, parameters)

    os.system(configure_string)

def make():
    ''' FIXME: Düzgün hale getirilecek '''
    os.system('make')

def install():
    ''' FIXME: Düzgün hale getirilecek '''
    ''' dir_suffix = /var/tmp/pisi/ _paket_adı_ /image/ '''

    dir_suffix = os.path.dirname(os.path.dirname(os.getcwd())) + \
        glb.const.install_dir_suffix
    
    install_string = 'make prefix=%s/%s install' % (dir_suffix, kde_dir)
    os.system(install_string)
