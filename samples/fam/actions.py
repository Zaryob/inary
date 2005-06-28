#!/usr/bin/python
# -*- coding: utf-8 -*-

from pisi.actionsapi import gnuconfig
from pisi.actionsapi import autotools
from pisi.actionsapi import libtoolize
from pisi.actionsapi import pisitools
from pisi.actionsapi import utils

def setup():
    utils.chmod('configure')
    gnuconfig.gnuconfig_update()
    libtoolize.libtoolize()
    autotools.configure()

def build():
    autotools.make()

def install():
    autotools.install()
    pisitools.dodoc('AUTHORS', 'ChangeLog', 'INSTALL' ,'NEWS', 'TODO', 'README')
