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
import pisi.context as ctx
from pisi.dependency import DepInfo
from pisi.util import Checks

__metaclass__ = xmlfile.autoxml


class Packager:
    t_Name = [xmlfile.String, xmlfile.mandatory]
    t_Email = [xmlfile.String, xmlfile.mandatory]
    def __str__(self):
        s = "%s <%s>" % (self.name, self.email)
        return s

        
class AdditionalFileInfo:
    s_Filename = xmlfile.mandatory
    a_Target = [xmlfile.String, xmlfile.mandatory]
    a_Permission = [xmlfile.String, xmlfile.optional]

    def __str__(self):
        s = "%s -> %s " % (self.filename, self.target)
        if self.permission:
            s += '(%s)' % self.permission
        return s

        
class Patch:
    s_Filename = xmlfile.mandatory
    a_compressionType = [xmlfile.String, xmlfile.optional]
    a_level = [xmlfile.String, xmlfile.optional]
    a_target = [xmlfile.String, xmlfile.optional]

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

    t_Date = [xmlfile.String, xmlfile.mandatory]
    t_Version = [xmlfile.String, xmlfile.mandatory]
    t_Release = [xmlfile.String, xmlfile.mandatory]
    t_Type = [xmlfile.String, xmlfile.optional]

    def __str__(self):
        s = self.date
        s += ", ver=" + self.version
        s += ", rel=" + self.release
        if self.type:
            s += ", type=" + self.type
        return s

        
class Path:
    s_Path = xmlfile.mandatory
    a_fileType =  [xmlfile.String, xmlfile.optional]

    def __str__(self):
        s = self.path
        s += ", type=" + self.fileType
        return s

class Dependency:
    t_Package = [xmlfile.String, xmlfile.mandatory]
    a_versionFrom = [xmlfile.String, xmlfile.optional]
    a_versionTo = [xmlfile.String, xmlfile.optional]
    a_releaseFrom = [xmlfile.String, xmlfile.optional]
    a_releaseTo = [xmlfile.String, xmlfile.optional]

    def __str__(self):
        s = self.package
        if self.versionFrom:
            s += 'ver >= ' + self.versionFrom
        if self.versionTo:
            s += 'ver <= ' + self.versionTo
        if self.releaseFrom:
            s += 'rel >= ' + self.releaseFrom
        if self.releaseTo:
            s += 'rel <= ' + self.releaseTo
        return s

class ComarProvide:

    s_om = [xmlfile.String, xmlfile.mandatory]
    a_script = [xmlfile.String, xmlfile.mandatory]

    def __str__(self):
        # FIXME: descriptive enough?
        s = self.script
        s += ' (' + self.om + ')'
        return s

        
class Archive:

    s_uri = [ xmlfile.String, xmlfile.mandatory ]
    a_type =[ xmlfile.String, xmlfile.mandatory ]
    a_sha1sum =[ xmlfile.String, xmlfile.mandatory ]

    def decode_post(self):
        self.name = basename(self.uri)


class Source:

    t_Name = [xmlfile.String, xmlfile.mandatory]
    t_HomePage = [xmlfile.String, xmlfile.mandatory]
    t_Packager = [Packager, xmlfile.mandatory]
    t_Summary = [xmlfile.String, xmlfile.mandatory]
    t_Description = [xmlfile.String, xmlfile.mandatory]
    t_License = [ [xmlfile.String], xmlfile.mandatory]
    t_IsA = [ [xmlfile.String], xmlfile.mandatory]
    t_PartOf = [xmlfile.String, xmlfile.mandatory]
    t_Archive = [Archive, xmlfile.mandatory ]
    t_Patch = [ [Patch], xmlfile.mandatory, "Patches/Patch"]
    t_BuildDep = [ [Dependency], xmlfile.mandatory, "BuildDependencies/Dependency"]
    t_History = [ [Update], xmlfile.mandatory, "History/Update"]

class AdditionalFile:
    s_filename = [xmlfile.String, xmlfile.mandatory]
    a_target = [xmlfile.String, xmlfile.mandatory]
    a_permission = [xmlfile.String, xmlfile.mandatory]

class Package:

    t_Name = [ xmlfile.String, xmlfile.mandatory ]
    t_Summary = [ xmlfile.String, xmlfile.mandatory ]
    t_Description = [ xmlfile.String, xmlfile.mandatory ]
    t_IsA = [ [xmlfile.String], xmlfile.mandatory]
    t_PartOf = [xmlfile.String, xmlfile.mandatory]
    t_History = [ [Update], xmlfile.mandatory, "History/Update"]
    t_Conflicts = [ [xmlfile.String], xmlfile.mandatory, "Conflicts/Package"]
    t_ProvidesComar = [ [ComarProvide], xmlfile.mandatory, "Provides/COMAR"]
    t_RequriesComar = [ [xmlfile.String], xmlfile.mandatory, "Requires/COMAR"]
    t_AdditionalFiles = [ [AdditionalFile], xmlfile.mandatory, "AdditionalFiles/AdditionalFile"]
    
