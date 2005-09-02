# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
# Authors:  Eray Ozkural <eray@uludag.org.tr>
#           Baris Metin <baris@uludag.org.tr>

"""
 Specfile module is our handler for PSPEC files. PSPEC (PISI SPEC)
 files are specification files for PISI source packages. This module
 provides read and write routines for PSPEC files.
"""

# standard python modules
from os.path import basename

# pisi modules
from pisi.xmlext import *
import pisi.xmlfile as xmlfile
from pisi.xmlfile import XmlFile
from pisi.ui import ui
from pisi.dependency import DepInfo
from pisi.util import Checks

__metaclass__ = xmlfile.autoxml


class Packager:
    t_Name = [types.StringType, xmlfile.mandatory]
    t_Email = [types.StringType, xmlfile.mandatory]
    def __str__(self):
        s = "%s <%s>" % (self.name, self.email)
        return s
        
        
class AdditionalFileInfo:
    s_Filename = xmlfile.mandatory
    a_Target = [types.StringType, xmlfile.mandatory]
    a_Permission = [types.StringType, xmlfile.optional]

    def __str__(self):
        s = "%s -> %s " % (self.filename, self.target)
        if self.permission:
            s += '(%s)' % self.permission
        return s

        
class Patch:
    s_Filename = xmlfile.mandatory
    a_compressionType = [types.StringType, xmlfile.optional]
    a_level = [types.StringType, xmlfile.optional]
    a_target = [types.StringType, xmlfile.optional]

    def __str__(self):
        s = self.filename
        if self.compressionType:
            s += ' (' + self.compressionType + ')'
        if self.level:
            s += ' level:' + self.level
        if self.target:
            s += ' target:' + self.target
        return s

        
class Update:

    t_Date = [types.StringType, xmlfile.mandatory]
    t_Version = [types.StringType, xmlfile.mandatory]
    t_Release = [types.StringType, xmlfile.mandatory]
    t_Type = [types.StringType, xmlfile.optional]

    def __str__(self):
        s = self.date
        s += ", ver=" + self.version
        s += ", rel=" + self.release
        if self.type:
            s += ", type=" + self.type
        return s

        
class Path:

    s_Path = xmlfile.mandatory
    a_fileType =  [types.StringType, xmlfile.optional]

    def __str__(self):
        s = self.pathname
        s += ", type=" + self.fileType
        return s


class ComarProvide:

    s_om = [types.StringType, xmlfile.mandatory]
    a_script = [types.StringType, xmlfile.mandatory]

    def __str__(self):
        # FIXME: descriptive enough?
        s = self.script
        s += ' (' + self.om + ')'
        return s

        
class Archive:

    s_uri = [ types.StringType, xmlfile.mandatory ]
    a_type =[ types.StringType, xmlfile.mandatory ]
    a_sha1sum =[ types.StringType, xmlfile.mandatory ]

    def decode_post(self):
        self.name = basename(self.uri)


class Source:

    t_Name = [types.StringType, xmlfile.mandatory]
    t_HomePage = [types.StringType, xmlfile.mandatory]
    t_Packager = [Packager, xmlfile.mandatory]
    t_Summary = [types.StringType, xmlfile.mandatory]
    t_Description = [types.StringType, xmlfile.mandatory]
    t_License = [ [types.StringType], xmlfile.mandatory]
    t_IsA = [ [types.StringType], xmlfile.mandatory]
    t_PartOf = [types.StringType, xmlfile.mandatory]
    t_Archive = [Archive, xmlfile.mandatory ]
    t_Patch = [ [Patch], xmlfile.mandatory, "Patches/Patch"]
    t_BuildDep = [ [Dependency], xmlfile.mandatory, "BuildDependencies/Dependency"]
    t_History = [ [Update], xmlfile.mandatory, "History/Update"]


class Package:

    t_Name = [ types.StringType, xmlfile.mandatory ]
    t_Summary = [ types.StringType, xmlfile.mandatory ]
    t_Description = [ types.StringType, xmlfile.mandatory ]
    t_IsA = [ [types.StringType], xmlfile.mandatory]
    t_PartOf = [types.StringType, xmlfile.mandatory]
    t_History = [ [Update], xmlfile.mandatory, "History/Update"]
    t_Conflicts = [ [types.StringType], xmlfile.mandatory, "Conflicts/Package"]
    t_ProvidesComar = [ [ComarProvide], xmlfile.mandatory, "Provides/COMAR"]
    t_RequriesComar = [ [types.StringType], xmlfile.mandatory, "Requires/COMAR"]
    t_AdditionalFiles = [ [AdditionalFile], xmlfile.mandatory, "AdditionalFiles/AdditionalFile"]
    
