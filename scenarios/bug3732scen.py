# -*- coding: utf-8 -*-
#
# Scenario : bug3732scen.py
#
# Source   : http://bugs.pardus.org.tr/show_bug.cgi?id=3732
#
# Problem  : If conflicting packages found while upgrading, by removing those prior to
#            fetching and installing the desktop may become unusable while upgrading
#            process
# 
# Problem Description: 
# 
# This problem appeared in our xorg package split process. The divided packages were
# all marked as conflicting packages to xorg package. But because the xorg package was
# a conflicting package, it is removed before any fetch operation and installing began.
# So some desktop processes could not be started or used properly until the upgrade 
# process ends.
#
# Expected:
#
# PiSi should not remove the conflicting packages unless fetching of all the new upgrade
# packages has finished.

from pisi.scenarioapi.scenario import *

XORG = "xorg"
QT = "qt"
XORG_SERVER = "xorg-server"
XORG_VIDEO = "xorg-video"
XORG_FONT = "xorg-font"

let_repo_had(XORG)
let_repo_had(QT, with_dependencies(XORG))
let_pisi_had(XORG, QT)

def run():
    repo_added_package(XORG_VIDEO, with_conflicts(XORG))
    repo_added_package(XORG_FONT, with_conflicts(XORG))
    repo_added_package(XORG_SERVER, with_conflicts(XORG), with_dependencies(XORG_VIDEO, XORG_FONT))
    repo_version_bumped(QT, with_removed_dependencies(XORG), with_added_dependencies(XORG_SERVER))
    repo_updated_index()
    pisi_upgraded()
