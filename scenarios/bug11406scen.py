# -*- coding: utf-8 -*-
#
# Scenario : bug11406scen.py
#
# Source   : http://bugs.pardus.org.tr/show_bug.cgi?id=11406
#

from pisi.scenarioapi.scenario import *

KERNEL = "kernel"
MODULE_A = "module-abc"
MODULE_B = "module-def"

let_repo_had(KERNEL, with_version("1.0"), with_requiring_actions("reverseDependencyUpdate"))
let_repo_had(MODULE_A, with_version("1.0"), with_added_dependency(KERNEL, version="1.0"))
let_repo_had(MODULE_B, with_version("1.0"), with_added_dependency(KERNEL, version="1.0"))

let_pisi_had(KERNEL, MODULE_A, MODULE_B)

def run():
    repo_version_bumped(KERNEL, with_version("2.0"))
    repo_version_bumped(MODULE_A, with_version("2.0"), with_added_dependency(KERNEL, version="2.0"))
    repo_version_bumped(MODULE_B,  with_version("2.0"), with_added_dependency(KERNEL, version="2.0"))
    repo_updated_index()
    pisi_upgraded(MODULE_A)
