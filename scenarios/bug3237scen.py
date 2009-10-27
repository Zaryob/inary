# -*- coding: utf-8 -*-
#
# Scenario : bug3237scen.py
#
# Source   : http://bugs.pardus.org.tr/show_bug.cgi?id=3237
#
# Problem  : If the revdep of the "upgraded only packages"' dependency is not satisfied
#            it is also added to the upgrade list and creates "confusion"
#
#            # pisi lu
#        amarok - KDE için müzik çalıcısı
#    ksynaptics - Synaptics touchpad yapılandırma aracı
#        libwmf - Microsoft Word gibi uygulamaların kullan.....
#      tunepimp - MusicBrainz uyumluluğu olan uygulamalar.......
#
#      pisi up tunepimp libwmf ksynaptics
#      Depolar güncelleniyor
#      * pardus-1.1 deposu güncelleniyor
#      pardus-1.1 deposu için güncelleme yok.
#      Aşağıdaki paketlerde çakışmalar bulunuyor: [amarok: lastfm-player  ile çakışıyor]
#      Bu çakışan paketler kaldırılsın mı? (evet/hayır)hayır
# 
# Problem Description: 
# 
# There appears to be some upgrades needed. We only wanted to upgrade some of the packages.
# But the package we did not include in the list of upgrades also is tried to be upgraded.
# The purpose to not include it in the upgrade list, was, it was conflicting with another 
# package.
#
# Expected:
#
# pisi either should not upgrade packages out of the given upgrade list or should show
# all the "to be upgraded" list before the conflict warning.

from pisi.scenarioapi.scenario import *

AMAROK = "amarok"
KSYNAPTICS = "ksynaptics"
LIBWMF = "libwmf"
TUNEPIMP = "tunepimp"
LASTFM = "lastfm-player"

let_repo_had(AMAROK, with_conflicts(LASTFM))
let_repo_had(LASTFM)
let_repo_had(TUNEPIMP, with_version("0.3.9"))
let_repo_had(KSYNAPTICS)
let_repo_had(LIBWMF)

let_pisi_had(AMAROK, LASTFM, TUNEPIMP, KSYNAPTICS, LIBWMF)

def run():
    repo_version_bumped(TUNEPIMP, with_version("0.4.1"))
    repo_version_bumped(AMAROK, with_added_dependency(TUNEPIMP, versionFrom="0.4.1"))
    repo_version_bumped(KSYNAPTICS)
    repo_version_bumped(LIBWMF)
    repo_updated_index()
    pisi_upgraded(LIBWMF, TUNEPIMP, KSYNAPTICS)
