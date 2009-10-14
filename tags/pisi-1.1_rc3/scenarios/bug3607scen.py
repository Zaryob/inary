# -*- coding: utf-8 -*-
#
# Scenario : bug3607scen.py
#
# Source   : http://bugs.pardus.org.tr/show_bug.cgi?id=3607
#
# Problem  : "pisi upgrade pkg" does not upgrade pkg's updated dependencies without --eager option
# 
# Problem Description: 
# 
# In the scenario we have 3 packages that yakuake depends kdebase and kdebase depends kdelibs. All
# the packages are version bumped at the repository. But when the user wants to upgrade yakuake
# with "pisi up yakuake" pisi should also upgrade the extra dependencies. This is done only with
# --eager option.
#
# Expected:
#
# --eager should be the default behaviour.
#

from pisi.scenarioapi.scenario import *

YAKUAKE = "yakuake"
KDEBASE = "kdebase"
KDELIBS = "kdelibs"

let_repo_had(YAKUAKE, with_dependencies(KDEBASE))
let_repo_had(KDEBASE, with_dependencies(KDELIBS))
let_repo_had(KDELIBS)

let_pisi_had(YAKUAKE, KDEBASE, KDELIBS)

def run():
    repo_version_bumped(KDEBASE)
    repo_version_bumped(KDELIBS)
    repo_version_bumped(YAKUAKE)
    repo_updated_index()
    pisi_upgraded(YAKUAKE)
