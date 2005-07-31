#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# Standard Python Modules
import os
import shutil

# Pisi-Core Modules
from pisi.ui import ui

# ActionsAPI Modules
from shelltools import chmod, makedirs
import get

def preplib(sourceDirectory):
    os.system('/sbin/ldconfig -n -N %s' % get.installDIR() + sourceDirectory)

def gnuconfig_update():
    ''' copy newest config.* onto source's '''
    shutil.copyfile('/usr/share/gnuconfig/config.sub', os.getcwd() + '/config.sub')
    shutil.copyfile('/usr/share/gnuconfig/config.guess',os.getcwd() + '/config.guess')

    ui.info('GNU Config Update Finished...\n')

def libtoolize():
    os.system('/usr/bin/libtoolize --copy --force')

def gen_usr_ldscript(dynamicLib):

    makedirs(get.installDIR() + '/usr/lib')

    destinationFile = open(get.installDIR() + '/usr/lib/' + dynamicLib, 'w')
    content = '''
/* GNU ld script
    Since Pardus has critical dynamic libraries
    in /lib, and the static versions in /usr/lib,
    we need to have a "fake" dynamic lib in /usr/lib,
    otherwise we run into linking problems.
*/
GROUP ( /lib/%s )
''' % dynamicLib

    destinationFile.write(content)
    destinationFile.close()
    chmod(get.installDIR() + '/usr/lib/' + dynamicLib)
