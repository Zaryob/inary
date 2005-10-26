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
    t_Homepage = [xmlfile.String, xmlfile.mandatory]
    t_Packager = [Packager, xmlfile.mandatory]
    t_Summary = [xmlfile.String, xmlfile.mandatory]
    t_Description = [xmlfile.String, xmlfile.mandatory]
    t_License = [ [xmlfile.String], xmlfile.mandatory]
    t_IsA = [ [xmlfile.String], xmlfile.mandatory]
    t_PartOf = [xmlfile.String, xmlfile.mandatory]
    t_Archive = [Archive, xmlfile.mandatory ]
    t_Patches = [ [Patch], xmlfile.mandatory]
    t_BuildDependencies = [ [Dependency], xmlfile.mandatory]


class Package:

    t_Name = [ xmlfile.String, xmlfile.mandatory ]
    t_Summary = [ xmlfile.String, xmlfile.mandatory ]
    t_Description = [ xmlfile.String, xmlfile.mandatory ]
    t_PartOf = [xmlfile.String, xmlfile.optional]
    t_IsA = [ [xmlfile.String], xmlfile.optional]
    t_Conflicts = [ [xmlfile.String], xmlfile.optional, "Conflicts/Package"]
    t_ProvidesComar = [ [ComarProvide], xmlfile.optional, "Provides/COMAR"]
    #t_RequriesComar = [ [xmlfile.String], xmlfile.mandatory, "Requires/COMAR"]
    t_AdditionalFiles = [ [AdditionalFile], xmlfile.optional]
    

class SpecFile(XmlFile):
    __metaclass__ = xmlfile.autoxml #needed when we specify a superclass

    tag = "PISI"

    t_Source = [ Source, xmlfile.mandatory]
    t_Packages = [ [Package], xmlfile.mandatory, "Package"]
    t_History = [ [Update], xmlfile.mandatory, "History/Update"]

    #we're not doing this with the init hook right now
    #def init(self, tag = "PISI"):
        #ignore tag
        #XmlFile.__init__(self, tag)

    def read(self, filename):
        """Read PSPEC file"""
        
        self.readxml(filename)
        
        errs = []
        self.decode(self.rootNode(), errs)
        if errs:
            raise Error(*errs)

        self.merge_tags()
        self.override_tags()

        #FIXME: copy only needed information
        # no need to keep full history with comments in metadata.xml
        self.source.history = self.history
        for p in self.packages:
            p.history = self.history

        self.unlink()

 
        errs = self.has_errors()
        if errs:
            e = ""
            for x in errs:
                e += x + "\n"
            raise XmlError(_("File '%s' has errors:\n%s") % (filename, e))

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

            if not pkg.partof:
                pkg.partof = self.source.partof

            if not pkg.license:
                pkg.license = self.source.license

            if not pkg.icon:
                pkg.icon = self.source.icon

            tmp.append(pkg)

        self.packages = tmp
        
    def merge_tags(self):
        """Merge tags from Source in Packages. Some tags in Packages merged
        with the tags from Source. There is a more detailed
        description in documents."""

        tmp = []
        for pkg in self.packages:

            if pkg.isa and self.source.isa:
                pkg.isa.append(self.source.isa)
            elif not pkg.isa and self.source.isa:
                pkg.isa = self.source.isa

            tmp.append(pkg)

        self.packages = tmp

    def has_errors(self):
        """Return errors of the PSPEC file if there are any."""
        #FIXME: has_errors name is misleading for a function that does
        #not just return a boolean value. check() would be better - exa
        err = Checks()
        err.join(self.source.has_errors())
        if len(self.packages) <= 0:
            errs.add(_("There should be at least one Package section"))
        for p in self.packages:
            err.join(p.has_errors())
        if len(self.history) <= 0:
            err.add(_("Source needs some education in History :)"))
        for update in self.history:
            err.join(update.has_errors())
        return err.list
    
    def write(self, filename):
        """Write PSPEC file"""
        self.newDOM()
        self.addChild(self.source.elt(self))
        for pkg in self.packages:
            self.addChild(pkg.elt(self))
        self.writexml(filename)
