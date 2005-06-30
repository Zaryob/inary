#!/usr/bin/python
# -*- coding: utf-8 -*-

from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools

def setup():
    pisitools.dosed('Makefile', 's:CFLAGS += -g:CFLAGS += -g -mcpu=i686 -O2 -pipe -fomit-frame-pointer:', '/CVSROOT =/d')

def build():
    autotools.make()

def install():
    pisitools.dosbin('logrotate')
    pisitools.doman('logrotate.8')
