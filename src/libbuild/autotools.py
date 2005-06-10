#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, pisiconfig

def configure():
	os.system( './configure --prefix=/usr \
				--host=i686-pc-linux-gnu \
				--mandir=/usr/share/man \
				--infodir=/usr/share/info \
				--datadir=/usr/share \
				--sysconfdir=/etc \
				--localstatedir=/var/lib ')

def make():
	os.system( 'make' )

def install():
	install_string = 'make prefix={D}/usr \
				datadir={D}/usr/share \
				infodir={D}/usr/share/info \
				localstatedir={D}/var/lib \
				mandir={D}/usr/share/man \
				sysconfdir={D}/etc \
				install'

	os.system( install_string.replace('{D}', pisiconfig.image_dir ) )
