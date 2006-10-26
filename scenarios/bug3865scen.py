# -*- coding: utf-8 -*-
#
# Scenario : bug3865scen.py
#
# Source   : http://bugs.pardus.org.tr/show_bug.cgi?id=3865
#
# Problem  : A need arised between the packages libmp4v2 and faad2 that libmp4v2 has to
#            define that it only conflicts with the faad2 until release 3.
#
# Problem Description: 
# 
# PiSi is incapable to define conflict versioning info. libmp4v2 only conflicts with faad2
# package's release no 3. But because PiSi does not understand that, two packages can not
# be installed together.
#
# Expected:
#
# Versioning info can be defined as in dependency informations.


from pisi.scenarioapi.scenario import *

LIBMP4V2 = "libmp4v2"
FAAD2 = "faad2"

let_repo_had(LIBMP4V2)
let_repo_had(FAAD2, with_version("0.2.1"))

let_pisi_had(LIBMP4V2, FAAD2)

def run():
    repo_version_bumped(LIBMP4V2, with_added_conflict(FAAD2, versionTo="0.2.1"))
    repo_version_bumped(FAAD2, with_version("0.2.5"))
    repo_updated_index()
    pisi_upgraded()
