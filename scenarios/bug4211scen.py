# -*- coding: utf-8 -*-
#
# Scenario : bug4211scen.py
#
# Source   : http://bugs.pardus.org.tr/show_bug.cgi?id=4211
#
# Problem  : PISI does not upgrade or install system.base packages before any other package
#
# Bağımlılıkları sağlamak için bu paketler verilen sırada kurulacaktır:
# util-macros xorg-proto xtrans libXdmcp libXau libX11 libXext libXp libICE libSM
# libXt libXprintUtil libXxf86vm ncurses less iputils gettext kbd sysvinit
# findutils popt gdbm 915resolution db3 mingetty splash-theme freetype fontconfig
# bzip2 expat zlib openssl python-fchksum db1 readline db4 python comar-api glib2
# pwdb cracklib pam shadow libperl perl attr acl coreutils debianutils sysklogd
# comar wireless-tools net-tools sed module-init-tools gawk which hdparm libpcre
# grep tcp-wrappers e2fsprogs util-linux bash baselayout flex unzip libidn cpio
# liblbxutil libdrm dhcpcd libfontenc libXfont libXfontcache libXxf86dga
# libXprintAppUtil libXfixes libXcomposite libXres libXrender libXv libXvMC libdmx
# libXmu libFS libXcursor libXtst libXpm libXaw libAppleWM libxkbfile libxkbui
# libWindowsWM libXi libXevie libXinerama libXdamage libXrandr libXxf86misc
# libXScrnSaver xbitmaps libXft libXTrap liboldX xorg-app xorg-data xorg-util
# xorg-input font-util xorg-font zorg jimmac-xcursor xorg-video xorg-server psmisc
# ddcxinfos texinfo groff groff-utf8 man man-pages coolplug mkinitramfs parted
# grub udev libgcc klibc lzma nss-mdns mudur gzip ncompress tar piksemel file
# python-bsddb3 pisi nano glibc lib-compat miscfiles libpng jpeg libcap
# openldap-client bc dmidecode fbgrab splashutils-misc splashutils pyparted
# openssh sysfsutils pcmciautils zip libusb linux-headers memtest86 procps curl
# vixie-cron slang usbutils pciutils
# Paket(ler)in toplam boyu: 65.91 MB
# Bağımlılıklar yüzünden ek paketler var. Devam etmek istiyor musunuz? (evet/hayır)e
# Paket util-macros, buildfarm deposunda bulundu
# util-macros-1.1.2-2-3.pisi     (5.0 KB)100%      0.00 B/s [??:??:??] [bitti]
# util-macros paketi, versiyon 1.1.2, sürüm 2, inşa 3 kuruluyor
# util-macros paketinin dosyaları arşivden çıkartılıyor
# util-macros paketi yapılandırılıyor
# util-macros paketi yapılandırıldı
# util-macros paketi kuruldu
# Paket xorg-proto, buildfarm deposunda bulundu
# xorg-proto-7.2_rc1-2-3.pisi    (190.0 KB)100%     77.64 KB/s [00:00:00] [bitti]
# Klavye kesmesi: Çıkıyor...
#
# Problem Description: 
# 
# In an upgrade or installation PiSi does not upgrade or install system.base packages before any
# other package.
#
# Expected:
#
# PiSi should update or install system.base packages before any other package on the system.
#

from pisi.scenarioapi.scenario import *

OPENOFFICE="openoffice"
SUN_JRE="sun-jre"
UTIL_MACROS="util-macros"
XORG_PROTO="xorg-proto"
COMAR="comar"
MUDUR="mudur"

let_repo_had(COMAR, with_partof("system.base"))
let_repo_had(MUDUR, with_partof("system.base"))
let_repo_had(UTIL_MACROS)
let_repo_had(XORG_PROTO)
let_repo_had(OPENOFFICE, with_dependencies(SUN_JRE))
let_repo_had(SUN_JRE)

let_pisi_had(UTIL_MACROS, XORG_PROTO, COMAR, MUDUR, OPENOFFICE, SUN_JRE)

def run():
    repo_version_bumped(SUN_JRE)
    repo_version_bumped(OPENOFFICE)
    repo_version_bumped(MUDUR)
    repo_version_bumped(COMAR)
    repo_version_bumped(XORG_PROTO)
    repo_version_bumped(UTIL_MACROS)

    repo_updated_index()
    pisi_upgraded(OPENOFFICE, SUN_JRE)

