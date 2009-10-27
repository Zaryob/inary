#!/usr/bin/python
#-*- coding: utf-8 -*-
#
# Copyright (C) 2006, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
# Authors:  Faik Uygur <faik@pardus.org.tr>

import os
import shutil
import glob
import sys

from pisi.scenarioapi.constants import *

def clean_out():
    for x in glob.glob(consts.repo_path + consts.glob_pisis):
        os.unlink(x)

    if os.path.exists(consts.pisi_db):
        shutil.rmtree(consts.pisi_db)

def run_scen(scenario):
    scenario()

def run_all():
    print '** Running all scenarios'
    for root, dirs, files in os.walk("."):
        scensources = filter(lambda x:x.endswith('scen.py'), files)
        for scensource in scensources:
            clean_out()
            running = "\n* Running scenario in %s\n" % scensource
            print running
            print len(running) * "=" + "\n"
            module = __import__(scensource[:len(scensource)-3])
            run_scen(module.run)

if __name__ == "__main__":
    os.chdir(consts.scenarios_path)

    args = sys.argv
    if len(args) > 1: 
        scens = sys.argv[1:]
        for scen in scens:
            clean_out()
            scen += 'scen.py'
            print "\n* Running scenario in %s\n" % scen
            module = __import__(scen[:len(scen)-3])
            run_scen(module.run)
    else: 
        run_all()
