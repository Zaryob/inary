# -*- coding: utf-8 -*-
#
# Copyright (C) 2008, TUBITAK/UEKAE
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
import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.pxml.autoxml as autoxml
import pisi.pxml.xmlfile as xmlfile
import pisi.context as ctx

__metaclass__ = autoxml.autoxml

class PackageInfo:

    a_version = [autoxml.String, autoxml.mandatory]
    a_release = [autoxml.String, autoxml.mandatory]
    a_build = [autoxml.String, autoxml.optional]

    def __str__(self):
        return self.version + "-" + self.release + "-" + (self.build or '?')

class Package:

    a_operation = [autoxml.String, autoxml.mandatory]
    a_type = [autoxml.String, autoxml.optional]

    t_Name = [autoxml.String, autoxml.mandatory]
    t_Before = [PackageInfo, autoxml.optional]
    t_After = [PackageInfo, autoxml.optional]

    def __str__(self):
        # "upgrade", "remove", "install", "reinstall", "downgrade"
        operation = ""
        if self.operation == "upgrade":
            if self.type == "delta":
                return _("%s is upgraded from %s to %s with delta.") % (self.name, self.before, self.after)
            else:
                return _("%s is upgraded from %s to %s.") % (self.name, self.before, self.after)
        elif self.operation == "remove":
            return _("%s %s is removed.") % (self.name, self.before)
        elif self.operation == "install":
            return _("%s %s is installed.") % (self.name, self.after)
        elif self.operation == "reinstall":
            return _("%s %s is reinstalled.") % (self.name, self.after)
        elif self.operation == "downgrade":
            return _("%s is downgraded from %s to %s.") % (self.name, self.before, self.after)
        else:
            return ""

class Operation:

    a_type = [autoxml.String, autoxml.mandatory]
    a_date = [autoxml.String, autoxml.mandatory]
    a_time = [autoxml.String, autoxml.mandatory]

    t_Packages = [ [Package], autoxml.mandatory, "Package"]

    def __str__(self):
        return self.type

class History(xmlfile.XmlFile):

    __metaclass__ = autoxml.autoxml

    tag = "PISI"

    t_Operation = [Operation, autoxml.mandatory]

    def create(self, operation):

        if operation not in ["upgrade", "remove", "emerge", "install", "snapshot", "takeback"]:
            raise Exception("Unknown package operation")

        opno = self._get_latest()
        self.histfile = "%s_%s.xml" % (opno, operation)

        year, month, day, hour, minute = time.localtime()[0:5]
        self.operation.type = operation
        self.operation.date = "%s-%02d-%02d" % (year, month, day)
        self.operation.time = "%02d:%02d" % (hour, minute)
        self.operation.no = opno

    # @param otype is currently only used to hold if an upgrade is from "delta"
    def add(self, pkgBefore=None, pkgAfter=None, operation=None, otype=None):

        if operation not in ["upgrade", "remove", "install", "reinstall", "downgrade", "snapshot"]:
            raise Exception("Unknown package operation")

        package = Package()
        package.operation = operation
        package.type = otype
        package.name = (pkgAfter and pkgAfter.name) or (pkgBefore and pkgBefore.name)

        if not pkgBefore:
            package.before = None

        if not pkgAfter:
            package.after = None

        for histInfo, pkgInfo in [(package.before, pkgBefore), (package.after, pkgAfter)]:
            if pkgInfo:
                histInfo.version = str(pkgInfo.version)
                histInfo.release = str(pkgInfo.release)
                histInfo.build = pkgInfo.build and str(pkgInfo.build)

        self.operation.packages.append(package)

    def update(self):
        self.write(os.path.join("%s/%s", ctx.config.history_dir(), self.histfile))

    def _get_latest(self):

        files = filter(lambda h:h.endswith(".xml"), os.listdir(ctx.config.history_dir()))
        if not files:
            return "001"

        files.sort(lambda x,y:int(x.split("_")[0]) - int(y.split("_")[0]))
        no, opxml = files[-1].split("_")
        return "%03d" % (int(no) + 1)
