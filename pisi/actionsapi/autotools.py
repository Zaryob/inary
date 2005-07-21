#!/usr/bin/python
# -*- coding: utf-8 -*-

# standard python modules
import os

# actions api modules
from actionglobals import glb

def configure(parameters = ''):
    ''' FIXME: Düzgün hale getirilecek '''
    ''' parameters = '--with-nls --with-libusb --with-something-usefull '''
    dirs = glb.dirs
    flags = glb.flags

    configure_string = './configure --prefix=/%s \
                --host=%s \
                --mandir=/%s \
                --infodir=/%s \
                --datadir=/%s \
                --sysconfdir=/%s \
                --localstatedir=/%s \
                %s' % (dirs.defaultprefix,
                       flags.host,
                       dirs.man,
                       dirs.info,
                       dirs.data,
                       dirs.conf,
                       dirs.localstate,
                       parameters)
    
    os.system(configure_string)

def rawConfigure(parameters = ''):
    os.system('./configure ' + parameters)

def compile(parameters = ''):
    compile_string = 'gcc ${CFLAGS} %s' % parameters
    os.system(compile_string)

def make(parameters = ''):
    ''' FIXME: Düzgün hale getirilecek '''
    make_string = 'make %s' % parameters
    os.system(make_string)

def install(parameters = ''):
    ''' FIXME: Düzgün hale getirilecek '''
    ''' dir_suffix = /var/tmp/pisi/ _paket_adı_ /image/ '''
    dirs = glb.dirs

    dir_suffix = os.path.dirname(os.path.dirname(os.getcwd())) + \
        glb.const.install_dir_suffix

    install_string = 'make prefix=%(prefix)s/%(defaultprefix)s \
                datadir=%(prefix)s/%(data)s \
                infodir=%(prefix)s/%(info)s \
                localstatedir=%(prefix)s/%(localstate)s \
                mandir=%(prefix)s/%(man)s \
                sysconfdir=%(prefix)s/%(conf)s \
                install' % {'prefix': dir_suffix,
                            'defaultprefix': dirs.defaultprefix,
                            'man': dirs.man,
                            'info': dirs.info,
                            'localstate': dirs.localstate,
                            'conf': dirs.conf,
                            'data': dirs.data}

    os.system(install_string)

def installWithPrefix(parameters = ''):
    dirs = glb.dirs

    dir_suffix = os.path.dirname(os.path.dirname(os.getcwd())) + \
        glb.const.install_dir_suffix

    install_string = 'make PREFIX=%s%s install' % (dir_suffix, parameters)

    os.system(install_string)

def installWithDestdir(parameters = ''):
    dirs = glb.dirs

    dir_suffix = os.path.dirname(os.path.dirname(os.getcwd())) + \
        glb.const.install_dir_suffix

    install_string = 'make install DESTDIR=%s %s' % (dir_suffix, parameters)

    os.system(install_string)

def installWithBasedir():
    dirs = glb.dirs

    dir_suffix = os.path.dirname(os.path.dirname(os.getcwd())) + \
        glb.const.install_dir_suffix

    install_string = 'make BASEDIR=%s install' % dir_suffix

    os.system(install_string)

def installWithInstallRootdir():
    dirs = glb.dirs

    dir_suffix = os.path.dirname(os.path.dirname(os.getcwd())) + \
        glb.const.install_dir_suffix

    install_string = 'make INSTALL_ROOT=%s install' % dir_suffix

    os.system(install_string)
