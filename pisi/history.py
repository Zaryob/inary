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
