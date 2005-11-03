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
#           Baris Metin <baris@uludag.org.tr

"""
Metadata module provides access to metadata.xml. metadata.xml is
generated during the build process of a package and used in the
installation. Package repository also uses metadata.xml for building
a package index.
"""

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.context as ctx
import pisi.specfile as specfile
import pisi.xmlfile as xmlfile
from pisi.util import Checks

class Source:
    __metaclass__ = xmlfile.autoxml

    t_Name = [xmlfile.String, xmlfile.mandatory]
    t_Homepage = [xmlfile.String, xmlfile.optional]
    t_Packager = [specfile.Packager, xmlfile.mandatory]

# FIXME: make inheritance work with autoxml (specfile.Package)
class Package:
    __metaclass__ = xmlfile.autoxml

    # FIXME: copied attributes
    t_Name = [ xmlfile.String, xmlfile.mandatory ]
    t_Summary = [ xmlfile.LocalText, xmlfile.optional ]
    t_Description = [ xmlfile.LocalText, xmlfile.optional ]
    t_IsA = [ [xmlfile.String], xmlfile.optional]
    t_PartOf = [xmlfile.String, xmlfile.optional]
    t_License = [ [xmlfile.String], xmlfile.optional]
    t_Icon = [ xmlfile.String, xmlfile.optional]
    t_RuntimeDependencies = [ [specfile.Dependency], xmlfile.optional]
    t_Files = [ [specfile.Path], xmlfile.optional]    
    t_Conflicts = [ [xmlfile.String], xmlfile.optional, "Conflicts/Package"]
    t_ProvidesComar = [ [specfile.ComarProvide], xmlfile.optional, "Provides/COMAR"]
    #t_RequiresComar = [ [xmlfile.String], xmlfile.mandatory, "Requires/COMAR"]
    t_AdditionalFiles = [ [specfile.AdditionalFile], xmlfile.optional]
    t_History = [ [specfile.Update], xmlfile.optional]

    t_Build = [ xmlfile.Integer, xmlfile.optional]
    t_Distribution = [ xmlfile.String, xmlfile.mandatory]
    t_DistributionRelease = [ xmlfile.String, xmlfile.mandatory]
    t_Architecture = [ xmlfile.String, xmlfile.mandatory]
    t_InstalledSize = [ xmlfile.Integer, xmlfile.mandatory]
    t_PackageURI = [ xmlfile.Integer, xmlfile.optional]

    def decode_hook(self, node, errs, where):
        self.version = self.history[0].version
        self.release = self.history[0].release

    def __str__(self):
        s = specfile.Package.__str__(self)
        return s

class MetaData(xmlfile.XmlFile):
    """Package metadata. Metadata is composed of Specfile and various
    other information. A metadata has two parts, Source and Package."""

    __metaclass__ = xmlfile.autoxml

    tag = "PISI"

    t_Source = [ Source, xmlfile.mandatory]
    t_Package = [ Package, xmlfile.mandatory]
    #t_History = [ [Update], xmlfile.mandatory]

    def from_spec(self, src, pkg):
        self.source.name = src.name
        self.source.homepage = src.homepage
        self.source.packager = src.packager
        self.package.name = pkg.name
        self.package.summary = pkg.summary
        self.package.description = pkg.description
        self.package.icon = pkg.icon
        self.package.isA = pkg.isA
        self.package.partOf = pkg.partOf
        self.package.license = pkg.license
        self.package.runtimeDependencies = pkg.runtimeDependencies
        self.package.files = pkg.files
        # FIXME: no need to copy full history with comments
        self.package.history = src.history
        self.package.conflicts = pkg.conflicts
        self.package.providesComar = pkg.providesComar
        #self.package.requiresComar = pkg.requiresComar
        self.package.additionalFiles = pkg.additionalFiles

        # FIXME: right way to do it?
        self.source.version = src.version
        self.source.release = src.release
        self.package.version = src.version
        self.package.release = src.release
