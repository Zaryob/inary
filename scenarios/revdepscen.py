# -*- coding: utf-8 -*-
#
# Scenario : revdepscen.py
#
# Source   : caglar@pardus.org.tr
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
# Package's reverse dependencies disappears unexpectedly.
#
# Expected:
#
# They should not. :)
#

from pisi.scenarioapi.scenario import *

KDELIBS = "kdelibs"
KOFFICE = "koffice"
KFTPGRABBER = "kftpgrabber"
KNETSTATS = "knetstats"
KONVERSATION = "konversation"
GWENVIEW = "gwenview"

let_repo_had(KDELIBS)
let_repo_had(KOFFICE, with_dependencies(KDELIBS))
let_repo_had(GWENVIEW, with_dependencies(KDELIBS))
let_repo_had(KFTPGRABBER, with_dependencies(KDELIBS))
let_repo_had(KNETSTATS, with_dependencies(KDELIBS))
let_repo_had(KONVERSATION, with_dependencies(KDELIBS))

let_pisi_had(KDELIBS, KOFFICE, GWENVIEW, KFTPGRABBER, KNETSTATS, KONVERSATION)

def run():
    pisi_info(KDELIBS)
    repo_version_bumped(KDELIBS)
    repo_updated_index()
    pisi_upgraded()
    pisi_info(KDELIBS)

