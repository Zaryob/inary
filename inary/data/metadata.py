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

"""
Metadata module provides access to metadata.xml. metadata.xml is
generated during the build process of a package and used in the
installation. Package repository also uses metadata.xml for building
a package index.
"""

# Inary Modules
import inary.util as util
import inary.data.specfile as specfile

# AutoXML Library
import inary.sxml.autoxml as autoxml
import inary.sxml.xmlfile as xmlfile

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class Delta(metaclass=autoxml.autoxml):
    t_PackageURI = [autoxml.String, autoxml.optional]
    t_PackageSize = [autoxml.Long, autoxml.optional]
    t_PackageHash = [autoxml.String, autoxml.optional, "SHA1Sum"]
    a_buildFrom = [autoxml.String, autoxml.optional]
    a_releaseFrom = [autoxml.String, autoxml.optional]


class Source(metaclass=autoxml.autoxml):
    t_Name = [autoxml.String, autoxml.mandatory]
    t_Homepage = [autoxml.String, autoxml.optional]
    t_Packager = [specfile.Packager, autoxml.mandatory]


class Package(specfile.Package, xmlfile.XmlFile, metaclass=autoxml.autoxml):
    t_Build = [autoxml.Integer, autoxml.optional]
    t_BuildHost = [autoxml.String, autoxml.optional]
    t_Distribution = [autoxml.String, autoxml.mandatory]
    t_DistributionRelease = [autoxml.String, autoxml.mandatory]
    t_Architecture = [autoxml.String, autoxml.mandatory]
    t_InstalledSize = [autoxml.Long, autoxml.mandatory]
    t_PackageSize = [autoxml.Long, autoxml.optional]
    t_PackageHash = [autoxml.String, autoxml.optional, "SHA1Sum"]
    t_InstallTarHash = [autoxml.String, autoxml.optional, "SHA1Sum"]
    t_PackageURI = [autoxml.String, autoxml.optional]
    t_DeltaPackages = [[Delta], autoxml.optional]
    t_PackageFormat = [autoxml.String, autoxml.optional]
    t_Rfp = [autoxml.String, autoxml.optional]
    t_PostOps = [autoxml.String, autoxml.optional]

    t_Source = [Source, autoxml.optional]

    def get_delta(self, release):
        for delta in self.deltaPackages:
            if delta.releaseFrom == str(release):
                return delta
        else:
            return None

    def decode_hook(self, node, errs, where):
        self.version = self.history[0].version
        self.release = self.history[0].release

    def __str__(self):
        s = specfile.Package.__str__(self)
        i_size = util.human_readable_size(self.installedSize)
        size = "%.2f %s" % (i_size[0], i_size[1])

        s += _('Distribution: {0}, Dist. Release: {1}\n').format(
            self.distribution, self.distributionRelease)
        s += _('Architecture: {0}, Installed Size: {1}').format(
            self.architecture, size)

        if self.packageSize:
            p_size = util.human_readable_size(self.packageSize)
            size = "%.2f %s" % (p_size[0], p_size[1])
            s += _(', Package Size: {}').format(size)

        s += _(', install.tar.xz sha1sum: {}').format(self.installTarHash)

        return s


class MetaData(xmlfile.XmlFile, metaclass=autoxml.autoxml):
    """Package metadata. Metadata is composed of Specfile and various
    other information. A metadata has two parts, Source and Package."""

    tag = "INARY"

    t_Source = [Source, autoxml.mandatory]
    t_Package = [Package, autoxml.mandatory]

    # t_History = [ [Update], autoxml.mandatory]

    def from_spec(self, src, pkg, history):
        # this just copies fields, it doesn't fix every necessary field
        self.source.name = src.name
        self.source.homepage = src.homepage
        self.source.packager = src.packager
        # FIXME: I know that replication sucks here, but this is the easiest
        # for now
        self.package.source = self.source
        self.package.rfp = src.rfp
        self.package.name = pkg.name
        self.package.summary = pkg.summary
        self.package.description = pkg.description
        self.package.icon = pkg.icon
        # merge pkg.isA with src.isA
        pkg.isA.extend(src.isA)
        self.package.isA = pkg.isA
        self.package.partOf = pkg.partOf
        self.package.license = pkg.license
        self.package.packageDependencies = pkg.packageDependencies
        self.package.packageAnyDependencies = pkg.packageAnyDependencies
        self.package.componentDependencies = pkg.componentDependencies
        self.package.files = pkg.files
        # Provides
        self.package.providesCommand = pkg.providesCommand
        self.package.providesCMAKE = pkg.providesCMAKE
        self.package.providesPkgConfig = pkg.providesPkgConfig
        self.package.providesService = pkg.providesService
        # FIXME: no need to copy full history with comments
        self.package.history = history
        self.package.conflicts = pkg.conflicts
        self.package.replaces = pkg.replaces
        self.package.additionalFiles = pkg.additionalFiles

        # FIXME: right way to do it?
        self.source.version = src.version
        self.source.release = src.release
        self.package.version = src.version
        self.package.release = src.release
