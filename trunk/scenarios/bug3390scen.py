# -*- coding: utf-8 -*-
#
# Scenario : bug3390scen.py
#
# Source   : http://bugs.pardus.org.tr/show_bug.cgi?id=3390
#
# Problem  : Package reverse dependencies are not updated in pisi database
#            
#            caglar@zangetsu ~ $ pisi info valgrind
#            Yüklü paket:
#            Ad: valgrind, versiyon 3.2.0, sürüm 5, inşa 4
#            Özet: Valgrind, x86-GNU/Linux ve ppc-GNU/Linux için geliştirilmiş, bellek
#            hatalarını ayıklayıcı, açık kaynaklı bir yazılımdır.
#            Açıklama: Valgrind, x86-GNU/Linux ve ppc-GNU/Linux için geliştirilmiş, bellek
#            hatalarını ayıklayıcı, açık kaynaklı bir yazılımdır.
#            Bileşen: programming.tools
#            Sağladıkları:
#            Bağımlılıklar:xorg openmpi
#            Dağıtım: Pardus, Dağıtım Sürümü: 1.1
#            Mimari: Any, Yerleşik Boyut: 19128120
#            Ters bağımlılıklar: kdesdk
# 
# Problem Description: 
#
# Valgrind package had a dependency of openmpi package. It is version bumped with removed
# dependeny of openmpi at the repository. Also openmpi is version bumped. After upgrading 
# pisi repository and trying to remove openmpi, it is seen that openmpi still has a reverse 
# dependency of valgrind.
#
# Expected:
#
# Pisi should have updated the reverse dependency informations correctly and should not show
# a reverse dependency of valgrind while removing openmpi, after a succesfull repository upgrade.

from pisi.scenarioapi.scenario import *

VALGRIND = "valgrind"
OPENMPI = "openmpi"

let_repo_had(VALGRIND, with_dependencies(OPENMPI))
let_repo_had(OPENMPI)
let_pisi_had(VALGRIND, OPENMPI)

def run():
    repo_version_bumped(VALGRIND, with_removed_dependencies(OPENMPI))
    repo_version_bumped(OPENMPI)
    repo_updated_index()
    pisi_upgraded()
    pisi_removed(OPENMPI)
