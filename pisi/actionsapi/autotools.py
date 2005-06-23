#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from pisi.context import const

def configure(parameters = None):
    ''' FIXME: Düzgün hale getirilecek '''
    ''' {EXTRA} = '--with-nls --with-libusb --with-something-usefull '''

    # FIXME: I don't think its feasible to write all these parameters
    # here. There should be a way to get all these... pisi.context.Constants?
    configure_string = './configure --prefix=/usr \
                --host=i686-pc-linux-gnu \
                --mandir=/usr/share/man \
                --infodir=/usr/share/info \
                --datadir=/usr/share \
                --sysconfdir=/etc \
                --localstatedir=/var/lib {EXTRA}'

    cmd = configure_string.replace('{EXTRA}', parameters)
    os.system(cmd)

def make():
    ''' FIXME: Düzgün hale getirilecek '''
    os.system('make')

def install():
    ''' FIXME: Düzgün hale getirilecek '''
    ''' {D} = /var/tmp/pisi/ _paket_adı_ /image/ '''
    global const

    install_string = 'make prefix={D}/usr \
                datadir={D}/usr/share \
                infodir={D}/usr/share/info \
                localstatedir={D}/var/lib \
                mandir={D}/usr/share/man \
                sysconfdir={D}/etc \
                install'

    cmd = os.path.dirname(os.path.dirname(os.getcwd())) + \
	const.install_dir_suffix
    cmd = install_string.replace('{D}', cmd)
    os.system(cmd)
