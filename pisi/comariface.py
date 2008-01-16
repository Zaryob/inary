# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import os
import time
import select

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx

class Error(pisi.Error):
    pass

try:
    import dbus
except ImportError:
    raise Error(_("dbus-python package is not fully installed"))

def is_char_valid(char):
    """Test if char is valid object path character."""
    char = ord(char)
    return (char in xrange(65, 91) or
           char in xrange(97, 123) or
           char in xrange(48, 58) or
           char == '_')

def make_object_path(package):
    """Generates DBus object name from package name."""
    object = package
    for char in package:
        if not is_char_valid(char):
            object = object.replace(char, '_')
    return object

def get_iface(package="", model=""):
    """Connect to the DBus daemon and return the system interface."""
    
    """
    sockname = "/var/run/comar.socket"
    # YALI starts comar chrooted in the install target, but uses PiSi outside of
    # the chroot environment, so PiSi needs to use a different socket path to be
    # able to connect true comar (usually /mnt/target/var/run/comar.socket).
    if ctx.comar_sockname:
        sockname = ctx.comar_sockname
    """
    
    if package:
        obj_path = "/package/%s" % package
    else:
        obj_path = "/"
    if model:
        obj_interface = "tr.org.pardus.comar.%s" % model
    else:
        obj_interface = "tr.org.pardus.comar"
    
    # This function is sometimes called when comar has recently started
    # or restarting after an update. So we give comar a chance to become
    # active in a reasonable time.
    timeout = 7
    while timeout > 0:
        try:
            bus = dbus.SystemBus()
            obj = bus.get_object("tr.org.pardus.comar", obj_path)
            iface = dbus.Interface(obj, dbus_interface=obj_interface)
            return iface
        except dbus.DBusException:
            pass
        time.sleep(0.2)
        timeout -= 0.2
    raise Error(_("cannot connect to dbus"))

def post_install(package_name, provided_scripts, scriptpath, metapath, filepath, fromVersion, fromRelease, toVersion, toRelease):
    """Do package's post install operations"""
    
    ctx.ui.info(_("Configuring %s package") % package_name)
    self_post = False
    sys_iface = get_iface()
    object_name = make_object_path(package_name)
    
    for script in provided_scripts:
        ctx.ui.debug(_("Registering %s comar script") % script.om)
        if script.om == "System.Package":
            self_post = True
        try:
            sys_iface.register(object_name, script.om, os.path.join(scriptpath, script.script))
        except dbus.DBusException, exception:
            raise Error, _("Script error: %s") % exception
    
    ctx.ui.debug(_("Calling post install handlers"))
    for handler in sys_iface.listModelApplications("System.PackageHandler"):
        iface = get_iface(handler, "System.PackageHandler")
        try:
            iface.setupPackage(metapath, filepath)
        except dbus.DBusException, exception:
            raise Error, _("Script error: %s") % exception
    
    if self_post:
        args = {
            "fromVersion": fromVersion,
            "fromRelease": fromRelease,
            "toVersion": toVersion,
            "toRelease": toRelease,
        }
        ctx.ui.debug(_("Running package's post install script"))
        try:
            iface = get_iface(object_name, "System.Package")
            iface.postInstall(fromVersion, toVersion, fromRelease, toRelease)
        except dbus.DBusException, exception:
            raise Error, _("Script error: %s") % exception

def pre_remove(package_name, metapath, filepath):
    """Do package's pre removal operations"""
    
    ctx.ui.info(_("Configuring %s package for removal") % package_name)
    sys_iface = get_iface()
    object_name = make_object_path(package_name)
    
    if "System.Package" in sys_iface.listApplicationModels(object_name):
        ctx.ui.debug(_("Running package's pre remove script"))
        iface = get_iface(handler_application, "System.PackageHandler")
        try:
            iface.preRemove()
        except dbus.DBusException, exception:
            raise Error, _("Script error: %s") % exception
    
    ctx.ui.debug(_("Calling pre remove handlers"))
    for handler in sys_iface.listModelApplications("System.PackageHandler"):
        iface = get_iface(handler, "System.PackageHandler")
        try:
            iface.cleanupPackage(metapath, filepath)
        except dbus.DBusException, exception:
            raise Error, _("Script error: %s") % exception
    
    ctx.ui.debug(_("Unregistering comar scripts"))
    try:
        sys_iface.remove(object_name)
    except dbus.DBusException, exception:
        raise Error, _("Script error: %s") % exception
