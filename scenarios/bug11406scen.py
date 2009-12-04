# -*- coding: utf-8 -*-
#
# Scenario : bug11406scen.py
#
# Source   : http://bugs.pardus.org.tr/show_bug.cgi?id=11406
#
# Problem  : reverse strict deps upgrading not working
#
# Problem Description: 
#
# pisi updates strict reverse deps if the reverse deps dependencies are not satisfied. For example if kernel is tried
# to be upgraded all the reverse deps are forced to be upgraded automatically. When only one rev-dep module is
# selected for an upgrade, kernel also comes as a strict dep for this module. But when kernel comes, all the rev-deps
# should come with kernel, too. It is not coming.
#
# This creates a problem for a user when he/she tries to update only her graphics card driver: kernel comes but none
# of the other drivers are updated. Sound becomes non-working as well as the other drivers.
#
# Expected:
#
# rev-deps of all the calculated to be upgraded packages should come


from pisi.scenarioapi.scenario import *

MODULE_ALSA_DRIVER = "module-alsa-driver"
MODULE_FGLRX = "module-fglrx"
KERNEL = "kernel"

let_repo_had(KERNEL, with_version("2.6.30"))
let_repo_had(MODULE_ALSA_DRIVER, with_added_dependency(KERNEL, version="2.6.30"))
let_repo_had(MODULE_FGLRX, with_added_dependency(KERNEL, version="2.6.30"))

let_pisi_had(KERNEL, MODULE_ALSA_DRIVER, MODULE_FGLRX)

def run():
    repo_version_bumped(KERNEL, with_version("2.6.31"))
    repo_version_bumped(MODULE_ALSA_DRIVER, with_added_dependency(KERNEL, version="2.6.31"))
    repo_version_bumped(MODULE_FGLRX, with_added_dependency(KERNEL, version="2.6.31"))
    repo_updated_index()
    pisi_upgraded(MODULE_FGLRX)
