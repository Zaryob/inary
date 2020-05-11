# -*- coding:utf-8 -*-
#
# Copyright (C) 2020, Sulin Community
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
# Developed by:
#   Ali Rıza Keskin (sulincix)
#   Suleyman Poyraz (Zaryob)
#

import os
import sys
# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext
sysconfdir="/var/lib/inary/sysconf"
def getmtime(path):
    """Get file or directory modify time"""
    if not os.path.exists(path):
        return 0
    return int(os.path.getmtime(path))


def getltime(name):
    """Get last modify time from database"""
    location = sysconfdir+"/{}".format(name)
    if not os.path.exists(sysconfdir):
        os.mkdir(sysconfdir)
    if not os.path.exists(location):
        setltime(name, 0)
    return int(open(location, "r").readline().replace("\n", ""))


def setltime(name, value):
    """Set last modify time to database"""
    location = sysconfdir+"/{}".format(name)
    open(location, "w").write(str(value))


def t(name, path, command):
    """Main trigger handler"""
    status = 0
    if os.path.isdir(path) == True:
        if getltime(name) != getmtime(path):
            sys.stdout.write(_("\n\x1b[33m    [-] Process triggering for \x1b[;0m{}".format(name)))
            status = os.system(command + " &>/dev/null")
            setltime(name, getmtime(path))
            if status != 0:
                sys.stdout.write("\r\x1b[K\x1b[31;1m    [!] Triggering end with \x1b[;0m{}".format(status))
            else:
                sys.stdout.write(_("\r\x1b[K\x1b[32;1m    [+] Process triggered for  \x1b[;0m{}".format(name)))
        

def t_r(name, path, command):
    """main trigger handler with recursive"""
    for i in os.listdir(path):
    	if os.path.isdir("{}/{}".format(path, i)):
             t("{}-{}".format(name, i), "{}/{}".format(path, i), "{}{}".format(command, i))


def proceed(force=False):
    sys.stdout.write(_("Process triggering for sysconf.\n"))
    if force:
        os.system("rm -rf {}".format(sysconfdir))
    t("fonts", "/usr/share/fonts", "fc-cache -f")
    t("glib-schema", "/usr/share/glib-2.0/schemas/", "glib-compile-schemas /usr/share/glib-2.0/schemas/")
    t_r("icon", "/usr/share/icons", "gtk-update-icon-cache -t -f /usr/share/icons/")
    t("desktop-database", "/usr/share/applications", "update-desktop-database /usr/share/applications")
    t("mandb", "/usr/share/man", "mandb cache-update")
    t_r("linux", "/lib/modules/", "depmod -a ")
    t("gdk-pixbuf", "/usr/lib/gdk-pixbuf-2.0/", "gdk-pixbuf-query-loaders --update-cache")
    t("mime", "/usr/share/mime", "update-mime-database /usr/share/mime")
    t("dbus", "/usr/share/dbus-1",
      "dbus-send --system --type=method_call --dest=org.freedesktop.DBus / org.freedesktop.DBUS.ReloadConfig")
    t("eudev", "/lib/udev/", "udevadm control --reload")
    t("gio-modules", "/usr/lib/gio/modules/", "gio-querymodules /usr/lib/gio/modules/")
    t("appstream", "/var/cache/app-info", "appstreamcli refresh-cache --force")
    t("ca-certficates", "/etc/ssl/certs", "update-ca-certificates --fresh")
    t("cracklib", "/usr/share/cracklib/", "create-cracklib-dict /usr/share/cracklib/*")
    sys.stdout.write("\n")
