#!/usr/bin/python
# -*- coding: utf-8 -*-

# standard python modules
import os
import string
import re
import shutil

# pisi modules
from pisi.ui import ui

# actions api modules
from shell import *

def gnuconfig_findnewest():
    ''' find the newest config.* file according to
    timestamp and return it'''

    locations = ['/usr/share/gnuconfig/config.sub',
		 '/usr/share/automake-1.9/config.sub',
		 '/usr/share/automake-1.8/config.sub',
		 '/usr/share/automake-1.7/config.sub',
		 '/usr/share/automake-1.6/config.sub',
		 '/usr/share/automake-1.5/config.sub',
		 '/usr/share/automake-1.4/config.sub',
         'share/config.sub']
    
    newer_location = {}

    for i in locations:
        if not os.path.exists(i):
            continue
        newer_location[i] = re.sub('\'', '',
                                   string.split((cat(i) | tr(str.rstrip)
                                   | grep ('^timestamp') 
                                   | join), '=')[1])

    keys = newer_location.keys()
    keys.sort()

    thelist=[]
    for i in keys:
        thelist.append((i, newer_location[i]))

    return os.path.dirname(thelist[0][0])

def gnuconfig_update():
    ''' copy newest config.* onto source's '''

    newer_location = gnuconfig_findnewest()

    try:
        shutil.copyfile(newer_location + '/config.sub',
            os.getcwd() + '/config.sub')
        shutil.copyfile(newer_location + '/config.guess',
            os.getcwd() + '/config.guess')
    except IOError, e:
        ui.error ("Error : %s\n" % e)
        sys.exit()

    ui.info('GNU Config Update Finished...\n')
