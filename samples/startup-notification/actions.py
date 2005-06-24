#!/usr/bin/python
# -*- coding: utf-8 -*-

from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools

def setup():
    autotools.configure()

def build():
    autotools.make()

def install():
    autotools.install()
    pisitools.dodoc('AUTHORS','ChangeLog','INSTALL', 'NEWS', 'README', 'doc/startup-notification.txt')
