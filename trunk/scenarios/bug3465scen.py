# -*- coding: utf-8 -*-
#
# Scenario : bug3465scen.py
#
# Source   : http://bugs.pardus.org.tr/show_bug.cgi?id=3465
#
# Problem  : Pisi does not warn the user about updated packages in the repository.
#
#            sudo pisi it wormux --reinstall
#            Bağımlılıkları sağlamak için bu paketler verilen sırada kurulacaktır:
#            wormux
#            Paketlerin toplam boyu: 17.62 MB
#            Paket wormux, pardus-1.1 deposunda bulundu
#            Program sonlandırıldı.
#            http://paketler.pardus.org.tr/pardus-1.1/wormux-0.7-2-1.pisi indirilemiyor; HTTP
#            Error 404: Not Found
# 
# Problem Description: 
#
# The user had not updated pisi's repository database for some time. Then, when pisi is asked 
# to reinstall an installed package, it failed to fetch the requested version of the package.
# Because the package had been upgraded at the repository and the old package has been removed.
#
# Expected:
#
# Pisi should warn the user to update repository.

from pisi.scenarioapi.scenario import *

WORMUX = "wormux"

let_repo_had(WORMUX)
let_pisi_had(WORMUX)

def run():
    repo_version_bumped(WORMUX)
    repo_updated_index()
    pisi_reinstalled(WORMUX)
