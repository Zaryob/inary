# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 - 2018, Suleyman POYRAZ (AquilaNipalensis)
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
import string

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary
import inary.context as ctx

class Error(inary.Error):
    pass

try:
    import scom
    import dbus
except ImportError:
    raise Error(_("scom-api package is not fully installed"))

def is_char_valid(char):
    """Test if char is valid object path character."""
    return char in string.ascii_letters + string.digits + "_"

def is_method_missing(exception):
    """Tells if exception is about missing method in SCOM script"""
    if exception._dbus_error_name in ("tr.org.sulin.scom.python.missing",
                                      "tr.org.sulin.scom.Missing"):
        return True
    return False

def safe_script_name(package):
    """Generates DBus-safe object name for package script names."""
    object = package
    for char in package:
        if not is_char_valid(char):
            object = object.replace(char, '_')
    if object[0].isdigit():
        object = '_%s' % object
    return object

def get_link():
    """Connect to the SCOM daemon and return the link."""

    sockname = "/var/run/dbus/system_bus_socket"
    # YALI starts scom chrooted in the install target, but uses INARY
    # outside of the chroot environment, so Inary needs to use a different
    # socket path to be able to connect true dbus (and scom).
    # (usually /var/run/dbus/system_bus_socket)
    if ctx.dbus_sockname:
        sockname = ctx.dbus_sockname

    alternate = False
    # If SCOM package is updated, all new configuration requests should be
    # made through new SCOM service. Passing alternate=True to Link() class
    # will ensure this.
    if ctx.scom_updated:
        alternate = True

    # This function is sometimes called when scom has recently started
    # or restarting after an update. So we give scom a chance to become
    # active in a reasonable time.
    timeout = 7
    exceptions = []
    while timeout > 0:
        try:
            link = scom.Link(socket=sockname, alternate=alternate)
            link.setLocale()
            return link
        except dbus.DBusException as e:
            exceptions.append(str(e))
        except Exception as e:
            exceptions.append(str(e))
        time.sleep(0.2)
        timeout -= 0.2
    raise Error(_("Cannot connect to SCOM: \n  %s\n")
                % "\n  ".join(exceptions))


def post_install(package_name, provided_scripts,
                 scriptpath, metapath, filepath,
                 fromVersion, fromRelease, toVersion, toRelease):
    """Do package's post install operations"""

    ctx.ui.info(_("Configuring %s package") % package_name)
    self_post = False

    package_name = safe_script_name(package_name)

    if package_name == 'scom':
        ctx.ui.debug(_("SCOM package updated. From now on,"
                       " using new SCOM daemon."))
        inary.api.set_scom_updated(True)

    link = get_link()

    for script in provided_scripts:
        ctx.ui.debug(_("Registering %s scom script") % script.om)
        script_name = safe_script_name(script.name) \
                if script.name else package_name
        if script.om == "System.Package":
            self_post = True
        try:
            link.register(script_name, script.om,
                          os.path.join(scriptpath, script.script))
        except dbus.DBusException as exception:
            raise Error(_("Script error: %s") % exception)
        if script.om == "System.Service":
            try:
                link.System.Service[script_name].registerState()
            except dbus.DBusException as exception:
                raise Error(_("Script error: %s") % exception)

    ctx.ui.debug(_("Calling post install handlers"))
    for handler in link.System.PackageHandler:
        try:
            link.System.PackageHandler[handler].setupPackage(
                    metapath,
                    filepath,
                    timeout=ctx.dbus_timeout)
        except dbus.DBusException as exception:
            # Do nothing if setupPackage method is not defined
            # in package script
            if not is_method_missing(exception):
                raise Error(_("Script error: %s") % exception)

    if self_post:
        if not fromVersion:
            fromVersion = ""
        if not fromRelease:
            fromRelease = ""

        ctx.ui.debug(_("Running package's post install script"))
        try:
            link.System.Package[package_name].postInstall(
                    fromVersion, fromRelease, toVersion, toRelease,
                    timeout=ctx.dbus_timeout)
        except dbus.DBusException as exception:
            # Do nothing if postInstall method is not defined in package script
            if not is_method_missing(exception):
                raise Error(_("Script error: %s") % exception)


def pre_remove(package_name, metapath, filepath):
    """Do package's pre removal operations"""

    ctx.ui.info(_("Running pre removal operations for %s") % package_name)
    link = get_link()

    package_name = safe_script_name(package_name)

    if package_name in list(link.System.Package):
        ctx.ui.debug(_("Running package's pre remove script"))
        try:
            link.System.Package[package_name].preRemove(
                    timeout=ctx.dbus_timeout)
        except dbus.DBusException as exception:
            # Do nothing if preRemove method is not defined in package script
            if not is_method_missing(exception):
                raise Error(_("Script error: %s") % exception)

    ctx.ui.debug(_("Calling pre remove handlers"))
    for handler in list(link.System.PackageHandler):
        try:
            link.System.PackageHandler[handler].cleanupPackage(
                    metapath, filepath, timeout=ctx.dbus_timeout)
        except dbus.DBusException as exception:
            # Do nothing if cleanupPackage method is not defined
            # in package script
            if not is_method_missing(exception):
                raise Error(_("Script error: %s") % exception)


def post_remove(package_name, metapath, filepath, provided_scripts=[]):
    """Do package's post removal operations"""

    ctx.ui.info(_("Running post removal operations for %s") % package_name)
    link = get_link()

    package_name = safe_script_name(package_name)
    scripts = set([safe_script_name(s.name) for s \
            in provided_scripts if s.name])
    scripts.add(package_name)

    if package_name in list(link.System.Package):
        ctx.ui.debug(_("Running package's postremove script"))
        try:
            link.System.Package[package_name].postRemove(
                    timeout=ctx.dbus_timeout)
        except dbus.DBusException as exception:
            # Do nothing if postRemove method is not defined in package script
            if not is_method_missing(exception):
                raise Error(_("Script error: %s") % exception)

    ctx.ui.debug(_("Calling post remove handlers"))
    for handler in list(link.System.PackageHandler):
        try:
            link.System.PackageHandler[handler].postCleanupPackage(
                    metapath, filepath, timeout=ctx.dbus_timeout)
        except dbus.DBusException as exception:
            # Do nothing if postCleanupPackage method is not defined
            # in package script
            if not is_method_missing(exception):
                raise Error(_("Script error: %s") % exception)

    ctx.ui.debug(_("Unregistering scom scripts"))
    for scr in scripts:
        try:
            link.remove(scr, timeout=ctx.dbus_timeout)
        except dbus.DBusException as exception:
            raise Error(_("Script error: %s") % exception)
