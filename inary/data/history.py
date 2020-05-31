# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2020, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# Standart Python Modules
import os
import time

# Inary Modules
import inary.context as ctx

# AutoXML Library
import inary.sxml.xmlfile as xmlfile
import inary.sxml.autoxml as autoxml

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class PackageInfo(metaclass=autoxml.autoxml):
    a_version = [autoxml.String, autoxml.mandatory]
    a_release = [autoxml.String, autoxml.mandatory]

    def __str__(self):
        # FIXME: Do not get these from the config file
        distro_id = ctx.config.values.general.distribution_id
        arch = ctx.config.values.general.architecture

        return "-".join((self.version, self.release, distro_id, arch))


class Repo(metaclass=autoxml.autoxml):
    a_operation = [autoxml.String, autoxml.mandatory]

    t_Name = [autoxml.String, autoxml.mandatory]
    t_Uri = [autoxml.String, autoxml.mandatory]

    def __str__(self):
        # "update", "remove", "add"
        if self.operation == "update":
            return _("{0} repository is updated.").format(self.name)
        elif self.operation == "add":
            pass  # TBD
        elif self.operation == "remove":
            pass  # TBD


class Package(metaclass=autoxml.autoxml):
    a_operation = [autoxml.String, autoxml.mandatory]
    a_type = [autoxml.String, autoxml.optional]

    t_Name = [autoxml.String, autoxml.mandatory]
    t_Before = [PackageInfo, autoxml.optional]
    t_After = [PackageInfo, autoxml.optional]

    def __str__(self):
        # "upgrade", "remove", "install", "reinstall", "downgrade"
        if self.operation == "upgrade":
            if self.type == "delta":
                return _("{0} is upgraded from {1} to {2} with delta.").format(
                    self.name, self.before, self.after)
            else:
                return _("{0} is upgraded from {1} to {2}.").format(
                    self.name, self.before, self.after)
        elif self.operation == "remove":
            return _("{0} {1} is removed.").format(self.name, self.before)
        elif self.operation == "install":
            return _("{0} {1} is installed.").format(self.name, self.after)
        elif self.operation == "reinstall":
            return _("{0} {1} is reinstalled.").format(self.name, self.after)
        elif self.operation == "downgrade":
            return _("{0} is downgraded from {1} to {2}.").format(
                self.name, self.before, self.after)
        else:
            return ""


class Operation(metaclass=autoxml.autoxml):
    a_type = [autoxml.String, autoxml.mandatory]
    a_date = [autoxml.String, autoxml.mandatory]
    a_time = [autoxml.String, autoxml.mandatory]

    t_Packages = [[Package], autoxml.optional, "Package"]
    t_Repos = [[Repo], autoxml.optional, "Repository"]

    def __str__(self):
        return self.type


class History(xmlfile.XmlFile, metaclass=autoxml.autoxml):
    tag = "INARY"

    t_Operation = [Operation, autoxml.mandatory]

    def create(self, operation):

        if operation not in ["downgrade", "upgrade", "remove", "emerge", "install", "snapshot", "takeback",
                             "repoupdate", "reset"]:
            raise Exception(_("Unknown package operation"))

        opno = self._get_latest()
        self.histfile = "{0}_{1}.xml".format(opno, operation)

        year, month, day, hour, minute = time.localtime()[0:5]
        self.operation.type = operation
        self.operation.date = "%s-%02d-%02d" % (year, month, day)
        self.operation.time = "%02d:%02d" % (hour, minute)
        self.operation.no = opno

    def update_repo(self, name, uri, operation=None):
        repo = Repo()
        repo.operation = operation
        repo.name = name
        repo.uri = uri
        self.operation.repos.append(repo)

    # @param otype is currently only used to hold if an upgrade is from "delta"
    def add(self, pkgBefore=None, pkgAfter=None, operation=None, otype=None):

        if operation not in ["upgrade", "remove",
                             "install", "reinstall", "downgrade", "snapshot"]:
            raise Exception(_("Unknown package operation"))

        package = Package()
        package.operation = operation
        package.type = otype
        package.name = (
            pkgAfter and pkgAfter.name) or (
            pkgBefore and pkgBefore.name)

        if not pkgBefore:
            package.before = None

        if not pkgAfter:
            package.after = None

        for histInfo, pkgInfo in [
                (package.before, pkgBefore), (package.after, pkgAfter)]:
            if pkgInfo:
                histInfo.version = str(pkgInfo.version)
                histInfo.release = str(pkgInfo.release)

        self.operation.packages.append(package)

    def update(self):
        self.write(os.path.join(ctx.config.history_dir(), self.histfile))

    @staticmethod
    def _get_latest():

        files = [
            h for h in os.listdir(
                ctx.config.history_dir()) if h.endswith(".xml")]
        if not files:
            return "001"

        # files.sort(key=lambda x,y:int(x.split("_")[0]) - int(y.split("_")[0]))
        files.sort(key=lambda x: int(x.split("_")[0].replace("0o", "0")))
        no = files[-1].replace("0o", "0").split("_")[0]
        return "%03d" % (int(no) + 1)
