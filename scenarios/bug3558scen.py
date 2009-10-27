# -*- coding: utf-8 -*-
#
# Scenario : bug3558scen.py
#
# Source   : http://bugs.pardus.org.tr/show_bug.cgi?id=3558
#
# Problem  : reverse dependency information disappears
#
# faik@iago scenarios $ pisi info kdelibs
# Yüklü paket:
# Ad: kdelibs, versiyon 3.5.4, sürüm 35, inşa 17
# Özet: Tüm KDE programlarının ihtiyaç duyduğu KDE kütüphaneleri
# Açıklama: Tüm KDE programlarının ihtiyaç duyduğu KDE kütüphaneleri
# Bileşen: desktop.kde.base
# Sağladıkları:
# Bağımlılıklar:qt arts freetype fontconfig libxslt libxml2 libpcre libart_lgpl libidn utempter alsa-lib cups tiff aspell 
# jasper mDNSResponder ghostscript acl zpspell openexr mit-kerberos tulliana2
# Dağıtım: Pardus, Dağıtım Sürümü: 1.1
# Mimari: Any, Yerleşik Boyut: 222414685
# Ters bağımlılıklar: kdebase gwenview
# 
# Problem Description: 
# 
# Package's reverse dependencies disappears unexpectedly. If a package which has reverse dependencies has been upgraded.
# The revdep list is removed from revdep db. So upgraded package will have an empty revdep list.
#
# Expected:
#
# They should not. :)
#

from pisi.scenarioapi.scenario import *

FLIGHTGEAR = "flightgear"
FLIGHTGEAR_DATA = "flightgear-data"

let_repo_had(FLIGHTGEAR, with_dependencies(FLIGHTGEAR_DATA))
let_repo_had(FLIGHTGEAR_DATA)

let_pisi_had(FLIGHTGEAR, FLIGHTGEAR_DATA)

def run():
    pisi_info(FLIGHTGEAR_DATA)
    repo_version_bumped(FLIGHTGEAR_DATA)
    repo_updated_index()
    pisi_upgraded()
    pisi_info(FLIGHTGEAR_DATA)
