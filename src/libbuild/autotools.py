#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

def configure( parameters = None):
	''' FIXME: Düzgün hale getirilecek '''
	''' {EXTRA} = '--with-nls --with-libusb --with-something-usefull '''

	configure_string = './configure --prefix=/usr \
				--host=i686-pc-linux-gnu \
				--mandir=/usr/share/man \
				--infodir=/usr/share/info \
				--datadir=/usr/share \
				--sysconfdir=/etc \
				--localstatedir=/var/lib {EXTRA}'

	os.system( configure_string.replace( '{EXTRA}', parameters ))

def make():
	''' FIXME: Düzgün hale getirilecek '''
	os.system( 'make' )

def install():
	''' FIXME: Düzgün hale getirilecek '''
	''' {D} = /var/tmp/pisi/ _paket_adı_ /image/ '''
	
	install_string = 'make prefix={D}/usr \
				datadir={D}/usr/share \
				infodir={D}/usr/share/info \
				localstatedir={D}/var/lib \
				mandir={D}/usr/share/man \
				sysconfdir={D}/etc \
				install'
	
	os.system( install_string.replace( '{D}', os.path.dirname( os.getcwd()) + '/image' ))
