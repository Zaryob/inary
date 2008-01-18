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

import time
import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.pxml.autoxml as autoxml
import pisi.pxml.xmlfile as xmlfile

__metaclass__ = autoxml.autoxml

class PackageInfo:

    a_version = [autoxml.String, autoxml.mandatory]
    a_release = [autoxml.String, autoxml.mandatory]
    a_build = [autoxml.String, autoxml.optional]

    def __str__(self):
        return self.version + "-" + self.release + "-" + self.build

class Package:

    a_operation = [autoxml.String, autoxml.mandatory]

    t_Name = [autoxml.String, autoxml.mandatory]
    t_Before = [PackageInfo, autoxml.optional]
    t_After = [PackageInfo, autoxml.optional]

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

    def initialize(self, operation):

        if operation not in ["upgrade", "remove", "install"]:
            raise Exception("Unknown package operation")

        year, month, day, hour, minute = time.localtime()[0:5]
        self.operation.type = operation
        self.operation.date = "%s-%02d-%02d" % (year, month, day)
        self.operation.time = "%02d:%02d" % (hour, minute)

    def add_operation(self, pkgBefore=None, pkgAfter=None, operation=None):

        if operation not in ["upgrade", "remove", "install"]:
            raise Exception("Unknown package operation")

        package = Package()
        package.operation = operation

        for histInfo, pkgInfo in [(package.before, pkgBefore), (package.after, pkgAfter)]:
            if pkgInfo:
                histInfo.version = pkgInfo.version
                histInfo.release = pkgInfo.release
                histInfo.build = pkgInfo.build

        self.operation.packages.append(package)
