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
import string

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
    return char in string.ascii_letters + string.digits + "_"

def make_object_path(package):
    """Generates DBus object name from package name."""
    object = package
    for char in package:
        if not is_char_valid(char):
            object = object.replace(char, '_')
    if object[0].isdigit():
        object = '_%s' % object
    return object

def get_iface(package="", model=""):
    """Connect to the DBus daemon and return the system interface."""
    
    sockname = "/var/run/dbus/system_bus_socket"
    # YALI starts comar chrooted in the install target, but uses PiSi outside of
    # the chroot environment, so PiSi needs to use a different socket path to be
    # able to connect true dbus (and comar).
    # (usually /var/run/dbus/system_bus_socket)
    if ctx.dbus_sockname:
        sockname = ctx.dbus_sockname
    
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
    exceptions = []
    while timeout > 0:
        try:
            bus = dbus.bus.BusConnection(address_or_type="unix:path=%s" % sockname)
            obj = bus.get_object(ctx.comar_destination, obj_path, introspect=False)
            iface = dbus.Interface(obj, dbus_interface=obj_interface)
            return iface
        except dbus.DBusException, e:
            exceptions.append(str(e))
            pass
        except Exception, e:
            exceptions.append(str(e))
            pass
        time.sleep(0.2)
        timeout -= 0.2
    raise Error(_("cannot connect to dbus: \n  %s\n") % "\n  ".join(exceptions))

def post_install(package_name, provided_scripts, scriptpath, metapath, filepath, fromVersion, fromRelease, toVersion, toRelease):
    """Do package's post install operations"""
    
    ctx.ui.info(_("Configuring %s package") % package_name)
    self_post = False
    sys_service = False
    sys_iface = get_iface()
    object_name = make_object_path(package_name)
    
    for script in provided_scripts:
        ctx.ui.debug(_("Registering %s comar script") % script.om)
        if script.om == "System.Package":
            self_post = True
        elif script.om == "System.Service":
            sys_service = True
        try:
            sys_iface.register(object_name, script.om, os.path.join(scriptpath, script.script))
        except dbus.DBusException, exception:
            raise Error, _("Script error: %s") % exception
        if sys_service:
            try:
                iface = get_iface(object_name, "System.Service")
                iface.registerState()
            except dbus.DBusException, exception:
                raise Error, _("Script error: %s") % exception
    
    ctx.ui.debug(_("Calling post install handlers"))
    for handler in sys_iface.listModelApplications("System.PackageHandler"):
        iface = get_iface(handler, "System.PackageHandler")
        try:
            iface.setupPackage(metapath, filepath, timeout=ctx.dbus_timeout)
        except dbus.DBusException, exception:
            # Do nothing if setupPackage method is not defined in package script
            if not (exception._dbus_error_name.startswith("tr.org.pardus.comar") and
               exception._dbus_error_name.split('tr.org.pardus.comar.')[1] == 'python.missing'):
                raise Error, _("Script error: %s") % exception
    
    if self_post:
        if not fromVersion:
            fromVersion = ""
        if not fromRelease:
            fromRelease = ""
        
        ctx.ui.debug(_("Running package's post install script"))
        try:
            iface = get_iface(object_name, "System.Package")
            iface.postInstall(fromVersion, fromRelease, toVersion, toRelease, timeout=ctx.dbus_timeout)
        except dbus.DBusException, exception:
            # Do nothing if postInstall method is not defined in package script
            if not (exception._dbus_error_name.startswith("tr.org.pardus.comar") and
               exception._dbus_error_name.split('tr.org.pardus.comar.')[1] == 'python.missing'):
                raise Error, _("Script error: %s") % exception
    
    if package_name == 'comar':
        pisi.api.set_comar_destination('tr.org.pardus.comar.new')

def pre_remove(package_name, metapath, filepath):
    """Do package's pre removal operations"""
    
    ctx.ui.info(_("Configuring %s package for removal") % package_name)
    sys_iface = get_iface()
    object_name = make_object_path(package_name)
    
    if "System.Package" in sys_iface.listApplicationModels(object_name):
        ctx.ui.debug(_("Running package's pre remove script"))
        iface = get_iface(object_name, "System.Package")
        try:
            iface.preRemove(timeout=ctx.dbus_timeout)
        except dbus.DBusException, exception:
            # Do nothing if preRemove method is not defined in package script
            if not (exception._dbus_error_name.startswith("tr.org.pardus.comar") and
                exception._dbus_error_name.split('tr.org.pardus.comar.')[1] == 'python.missing'):
                raise Error, _("Script error: %s") % exception
    
    ctx.ui.debug(_("Calling pre remove handlers"))
    for handler in sys_iface.listModelApplications("System.PackageHandler"):
        iface = get_iface(handler, "System.PackageHandler")
        try:
            iface.cleanupPackage(metapath, filepath, timeout=ctx.dbus_timeout)
        except dbus.DBusException, exception:
            # Do nothing if cleanupPackage method is not defined in package script
            if not (exception._dbus_error_name.startswith("tr.org.pardus.comar") and
               exception._dbus_error_name.split('tr.org.pardus.comar.')[1] == 'python.missing'):
                raise Error, _("Script error: %s") % exception
    
    ctx.ui.debug(_("Unregistering comar scripts"))
    try:
        sys_iface.remove(object_name)
    except dbus.DBusException, exception:
        raise Error, _("Script error: %s") % exception
