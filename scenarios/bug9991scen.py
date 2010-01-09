# -*- coding: utf-8 -*-
#
# Scenario : bug9991scen.py
#
# Source   : http://bugs.pardus.org.tr/show_bug.cgi?id=9991
#
# Problem  : blacklisted system.base packages are still upgraded
#
# Problem Description:
#
# We may assume that the users which are aware of the blacklisting feature are totally aware of the consequences of
# blacklisting a system.base package. Current code forces the upgrade of system.base packages even it's blacklisted.
#
# Expected:
#
# All blacklisted packages should be excluded from upgrade plans.


from pisi.scenarioapi.scenario import *

DBUS = "dbus"
GRUB = "grub"
PISI = "pisi"
KERNEL = "kernel"
BLUEZ = "bluez"

let_repo_had(KERNEL)
let_repo_had(BLUEZ)
let_repo_had(DBUS, with_partof("system.base"))
let_repo_had(PISI, with_partof("system.base"))
let_pisi_had(DBUS, PISI, KERNEL, BLUEZ)

def run():
    repo_version_bumped(KERNEL)
    repo_version_bumped(BLUEZ)
    repo_version_bumped(DBUS)
    repo_version_bumped(PISI)
    repo_updated_index()

    # The packages in /etc/pisi/blacklist should not be upgraded
    pisi_upgraded()
