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

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

# standard python modules
from os.path import basename

# pisi modules
from pisi.xmlext import *
import pisi.xmlfile as xmlfile
from pisi.xmlfile import XmlFile
import pisi.context as ctx
from pisi.dependency import Dependency
import pisi.dependency
from pisi.util import Checks
import pisi.util as util

class Error(pisi.Error):
    pass

__metaclass__ = xmlfile.autoxml

class Packager:

    t_Name = [xmlfile.Text, xmlfile.mandatory]
    t_Email = [xmlfile.String, xmlfile.mandatory]
    def __str__(self):
        s = "%s <%s>" % (self.name, self.email)
        return s


class AdditionalFile:

    s_Filename = [xmlfile.String, xmlfile.mandatory]
    a_Target = [xmlfile.String, xmlfile.mandatory]
    a_Permission = [xmlfile.String, xmlfile.optional]

    def __str__(self):
        s = "%s -> %s " % (self.filename, self.target)
        if self.permission:
            s += '(%s)' % self.permission
        return s

        
class Patch:
    
    s_Filename = [xmlfile.String, xmlfile.mandatory]
    a_compressionType = [xmlfile.String, xmlfile.optional]
    a_level = [xmlfile.Integer, xmlfile.optional]
    a_target = [xmlfile.String, xmlfile.optional]

    #FIXME: what's the cleanest way to give a default value for reading level?
    #def decode_hook(self, node, errs, where):
    #    if self.level == None:
    #        self.level = 0

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
    
    a_release = [xmlfile.String, xmlfile.mandatory]
    t_Date = [xmlfile.String, xmlfile.mandatory]
    t_Version = [xmlfile.String, xmlfile.mandatory]
    t_Type = [xmlfile.String, xmlfile.optional]

    def __str__(self):
        s = self.date
        s += ", ver=" + self.version
        s += ", rel=" + self.release
        if self.type:
            s += ", type=" + self.type
        return s

        
class Path:

    s_Path = [xmlfile.String, xmlfile.mandatory]
    a_fileType =  [xmlfile.String, xmlfile.optional]

    def __str__(self):
        s = self.path
        s += ", type=" + self.fileType
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

    def decode_hook(self, node, errs, where):
        self.name = basename(self.uri)


class Source:

    t_Name = [xmlfile.String, xmlfile.mandatory]
    t_Homepage = [xmlfile.String, xmlfile.optional]
    t_Packager = [Packager, xmlfile.mandatory]
    t_Summary = [xmlfile.LocalText, xmlfile.mandatory]
    t_Description = [xmlfile.LocalText, xmlfile.mandatory]
    t_IsA = [ [xmlfile.String], xmlfile.mandatory]
    t_PartOf = [xmlfile.String, xmlfile.mandatory]
    t_Icon = [ xmlfile.String, xmlfile.optional]
    t_License = [ [xmlfile.String], xmlfile.mandatory]
    t_Archive = [Archive, xmlfile.mandatory ]
    t_Patches = [ [Patch], xmlfile.optional]
    t_BuildDependencies = [ [Dependency], xmlfile.optional]
    t_Version = [ xmlfile.String, xmlfile.optional]
    t_Release = [ xmlfile.String, xmlfile.optional]


class Package:

    t_Name = [ xmlfile.String, xmlfile.mandatory ]
    t_Summary = [ xmlfile.LocalText, xmlfile.optional ]
    t_Description = [ xmlfile.LocalText, xmlfile.optional ]
    t_IsA = [ [xmlfile.String], xmlfile.optional]
    t_PartOf = [xmlfile.String, xmlfile.optional]
    t_License = [ [xmlfile.String], xmlfile.optional]
    t_Icon = [ xmlfile.String, xmlfile.optional]
    t_RuntimeDependencies = [ [Dependency], xmlfile.optional]
    t_Files = [ [Path], xmlfile.optional]    
    t_Conflicts = [ [xmlfile.String], xmlfile.optional, "Conflicts/Package"]
    t_ProvidesComar = [ [ComarProvide], xmlfile.optional, "Provides/COMAR"]
    #t_RequiresComar = [ [xmlfile.String], xmlfile.mandatory, "Requires/COMAR"]
    t_AdditionalFiles = [ [AdditionalFile], xmlfile.optional]
    t_History = [ [Update], xmlfile.optional]
    
    def pkg_dir(self):
        packageDir = self.name + '-' \
                     + self.version + '-' \
                     + self.release

        return util.join_path( ctx.config.lib_dir(), packageDir)

    def installable(self):
        """calculate if pkg is installable currently"""
        deps = self.runtimeDependencies
        return pisi.dependency.satisfies_dependencies(self.name, deps)

class SpecFile(XmlFile):
    __metaclass__ = xmlfile.autoxml #needed when we specify a superclass

    tag = "PISI"

    t_Source = [ Source, xmlfile.mandatory]
    t_Packages = [ [Package], xmlfile.mandatory, "Package"]
    t_History = [ [Update], xmlfile.mandatory]

    #we're not doing this with the init hook right now
    #def init(self, tag = "PISI"):
        #ignore tag
        #XmlFile.__init__(self, tag)

    def read_hook(self, errs):
        """Read PSPEC file"""
        self.merge_tags()
        self.override_tags()

    def merge_tags(self):
        """Merge tags from Source in Packages. Some tags in Packages merged
        with the tags from Source. There is a more detailed
        description in documents."""

        # FIXME: copy only needed information
        # no need to keep full history with comments in metadata.xml
        self.source.history = self.history

        # To avoid tag duplication in PSPEC we need to get 
        # the last version and release information
        # from the most recent History/Update.
        if not self.source.version:
            self.source.version = self.history[0].version
        if not self.source.release:
            self.source.release = self.history[0].release

        tmp = []
        for pkg in self.packages:
            pkg.isA.extend(self.source.isA)
            pkg.history = self.history
            tmp.append(pkg)
        self.packages = tmp

    def override_tags(self):
        """Override tags from Source in Packages. Some tags in Packages
        overrides the tags from Source. There is a more detailed
        description in documents."""

        tmp = []
        for pkg in self.packages:
            if not pkg.summary:
                pkg.summary = self.source.summary
            if not pkg.description:
                pkg.description = self.source.description
            if not pkg.partOf:
                pkg.partOf = self.source.partOf
            if not pkg.license:
                pkg.license = self.source.license
            if not pkg.icon:
                pkg.icon = self.source.icon
            tmp.append(pkg)
        self.packages = tmp
