#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

from inary.actionsapi import cmaketools
from inary.actionsapi import inarytools
from inary.actionsapi import shelltools
from inary.actionsapi import get

WorkDir = "hello-cmake"

def setup():
    cmaketools.configure()
    
def build():
    cmaketools.make()

def install():
    autotools.install()            

    inarytools.dodir("/var/opt/helloworld")
    
    inarytools.dodoc("doc/hellodoc")

    inarytools.doexe("helloworld", "/var/opt/helloworld")    

    inarytools.doinfo("doc/*")

    inarytools.dolib("src/helloworld.o")

    '''/opt/hello'''
    inarytools.insinto("/var/opt/", "src/helloworld", "hello")
    '''/opt/hi'''
    inarytools.insinto("/var/opt/", "src/helloworld", "hi")

    inarytools.domove("/var/opt/hello", "/opt/")

    inarytools.domove("/opt/hi", "/var/", "goodbye")

    inarytools.dobin("helloworld")

    inarytools.dobin("helloworld", "/bin")

    inarytools.dosbin("helloworld")

    inarytools.dosbin("helloworld", "/sbin")

    inarytools.dosed("src/helloworld.cpp", "Hello world", "Goodbye world")

    inarytools.dosym("helloworld", "/usr/sbin/goodbye")

    inarytools.dosym("helloworld", "/usr/bin/goodbye")

    inarytools.dodir("/home/skeletuser")

    inarytools.removeDir("/home/skeletuser")

    inarytools.removeDir("/home")

    inarytools.newdoc("src/helloworld.cpp", "goodbyeworld.cpp")

    shelltools.touch("%s/opt/sulin" % get.installDIR())

    shelltools.copy("%s/opt/sulin" % get.installDIR(), "%s/opt/skelet" % get.installDIR())

    shelltools.move("%s/opt/sulin" % get.installDIR(), "%s/opt/SULIN" % get.installDIR())

    shelltools.copytree("%s/opt/" % get.installDIR(), "%s/sys/" % get.installDIR())

    shelltools.unlink("%s/sys/helloworld/helloworld" % get.installDIR())
 
    shelltools.unlinkDir("%s/sys/helloworld" % get.installDIR())
    
    libtools.gen_usr_ldscript("helloworld.o")
