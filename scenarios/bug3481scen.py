# -*- coding: utf-8 -*-
#
# Scenario : bug3481scen.py
#
# Source   : http://bugs.pardus.org.tr/show_bug.cgi?id=3481
#
# Problem  : PISI asks if conflicting system.base application to be removed but does not
#            allow it without -S
#
#            Aşağıdaki paketlerde çakışmalar bulunuyor: [coreutils: hashalot  ile çakışıyor]
#            Bu çakışan paketler kaldırılsın mı? (evet/hayır)evet
#            Emniyet mandalı: taban sistem system.base deki bu paketler kaldırılamıyor: hashalot
#            Kaldıracak paket yok.
#            Program sonlandırıldı.
#            pisi.operations.Error: Çakışmalar var
#            Genel yardım için lütfen 'pisi help' komutunu kullanınız.
#
# Problem Description: 
# 
# PISI upgrade command sees some system.base packages conflict with each other. It asks if you 
# want to remove the conflicting package but does not allow it to be removed without 
# --bypass-safety parameter.
#
# Expected:
#
# Pisi should remove the package if answered yes.
#

from pisi.scenarioapi.scenario import *

HASHALOT="hashalot"
COREUTILS="coreutils"
GLIBC="glibc"
UTIL_LINUX="util-linux"

let_repo_had(HASHALOT, with_partof("system.base"))
let_repo_had(COREUTILS, with_partof("system.base"))
let_repo_had(GLIBC, with_partof("system.base"))
let_repo_had(UTIL_LINUX, with_partof("system.base"))

let_pisi_had(COREUTILS, HASHALOT, GLIBC, UTIL_LINUX)

def run():
    repo_version_bumped(GLIBC)
    repo_version_bumped(UTIL_LINUX)
    repo_version_bumped(COREUTILS, with_added_conflicts(HASHALOT))
    repo_updated_index()
    pisi_upgraded()
