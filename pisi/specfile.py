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
#           Gurer Ozen <gurer@uludag.org.tr>
#           Baris Metin <baris@uludag.org.tr>
# History:
# Baris wrote the first version, then Baris and Eray did
# several revisions of it. It was modified in accordance
# with Gurer's observations about poor error handling.


"""
Specfile module is our handler for PSPEC files. PSPEC (PISI SPEC)
files are specification files for PISI source packages. This module
provides read and write access to PSPEC files.
"""

# standard python modules
from os.path import basename

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

# pisi modules
import pisi
from pisi.xmlext import *
from pisi.xmlfile import XmlFile
from pisi.dependency import DepInfo
from pisi.util import Checks

#class Packager:
#    __metaclass__ = xmlfile.autoxml

class PackagerInfo:
    def __init__(self, node = None):
        if node:
            self.name = getNodeText(getNode(node, "Name"))
            self.email = getNodeText(getNode(node, "Email"))
        else:
            self.name = None
            self.email = None

    def elt(self, xml):
        node = xml.newNode("Packager")
        xml.addTextNodeUnder(node, "Name", self.name)
        xml.addTextNodeUnder(node, "Email", self.email)
        return node

    def has_errors(self):
        err = Checks()
        err.has_tag(self.name, "Packager", "Name")
        err.has_tag(self.email, "Packager", "Email")
        return err.list

    def __str__(self):
        s = "%s <%s>" % (self.name, self.email)
        return s

class AdditionalFileInfo:
    def __init__(self, node = None):
        if node:
            self.filename = getNodeText(node)
            self.target = getNodeAttribute(node, "target")
            self.permission = getNodeAttribute(node, "permission")

    def elt(self, xml):
        node = xml.newNode("AdditionalFile")
        xml.addText(node, self.filename)
        node.setAttribute("target", self.target)
        if self.permission:
            node.setAttribute("permission", self.permission)

    def has_errors(self):
        err = Checks()
        if not self.filename:
            err.add(_("AdditionalFile should have file name string"))
        if not self.target:
            err.add(_("AdditionalFile should have a target attribute"))
        return err.list

    def __str__(self):
        s = "->".join(self.filename, self.target)
        s += s + '(' + self.permission + ')'
        return s

class PatchInfo:
    def __init__(self, node = None):
        if node:
            self.filename = getNodeText(node)
            self.compressionType = getNodeAttribute(node, "compressionType")
            self.level = getNodeAttribute(node, "level")
            self.target = getNodeAttribute(node, "target")
        else:
            self.compressionType = None
        if not self.level:
            self.level = 0
        else:
            self.level = int(self.level)
        if not self.target:
            self.target = ''

    def elt(self, xml):
        node = xml.newNode("Patch")
        xml.addText(node, self.filename)
        if self.compressionType:
            node.setAttribute("compressionType", self.compressionType)
        if self.level:
            node.setAttribute("level", str(self.level))
        if self.target:
            node.setAttribute("target", self.target)
        return node

    def has_errors(self):
        if not self.filename:
            return [ _("Patch should have a filename string") ]
        return None

    def __str__(self):
        s = self.filename
        s += ' (' + self.compressionType + ')'
        s += ' level:' + self.level
        return s


class UpdateInfo:
    def __init__(self, node = None):
        if node:
            self.date = getNodeText(getNode(node, "Date"))
            self.version = getNodeText(getNode(node, "Version"))
            self.release = getNodeText(getNode(node, "Release"))
            self.type = getNodeText(getNode(node, "Type"))
        else:
            self.type = None

    def elt(self, xml):
        node = xml.newNode("Update")
        xml.addTextNodeUnder(node, "Date", self.date)
        xml.addTextNodeUnder(node, "Version", self.version)
        xml.addTextNodeUnder(node, "Release", self.release)
        if self.type:
                xml.addTextNodeUnder(node, "Type", self.type)
        return node

    def has_errors(self):
        err = Checks()
        err.has_tag(self.date, "Update", "Date")
        err.has_tag(self.version, "Update", "Version")
        err.has_tag(self.release, "Update", "Release")
        return err.list

    def __str__(self):
        s = self.date
        s += ", ver=" + self.version
        s += ", rel=" + self.release
        s += ", type=" + self.type
        return s

class PathInfo:
    def __init__(self, node = None):
        if node:
            self.pathname = getNodeText(node)
            self.fileType = getNodeAttribute(node, "fileType")
        if not self.fileType:
            self.fileType = "other"

    def elt(self, xml):
        node = xml.newNode("Path")
        xml.addText(node, self.pathname)
        node.setAttribute("fileType", self.fileType)
        return node

    def has_errors(self):
        if not self.pathname:
            return [ _("Path tag should have a name string") ]
        return None

    def __str__(self):
        s = self.pathname
        s += ", type=" + self.fileType
        return s

class ComarProvide:
    def __init__(self, node = None):
        if node:
            self.om = getNodeText(node)
            self.script=getNodeAttribute(node, "script")

    def elt(self, xml):
        node = xml.newNode("COMAR")
        xml.addText(node, self.om)
        node.setAttribute("script", self.script)
        return node

    def has_errors(self):
        if not self.om or not self.script:
            return [ _("COMAR provide should have something :)") ]
        return None

    def __str__(self):
        s = self.script
        s += ' (' + self.om + ')'
        return s

class SourceInfo:
    """A structure to hold source information. Source information is
    located under <Source> tag in PSPEC file."""
    def __init__(self, node = None):
        if node:
            self.name = getNodeText(node, "Name")
            self.homepage = getNodeText(node, "Homepage")
            self.packager = PackagerInfo(getNode(node, "Packager"))
            self.summary = getNodeText(node, "Summary")
            self.description = getNodeText(node, "Description")
            self.license = map(getNodeText, getAllNodes(node, "License"))
            self.icon = getNodeText(node, "Icon")
            self.isa = map(getNodeText, getAllNodes(node, "IsA"))
            self.partof = getNodeText(node, "PartOf")
            archiveNode = getNode(node, "Archive")
            self.archiveUri = getNodeText(archiveNode).strip()
            self.archiveName = basename(self.archiveUri)
            self.archiveType = getNodeAttribute(archiveNode, "type")
            self.archiveSHA1 = getNodeAttribute(archiveNode,
                                                "sha1sum")
            patchElts = getAllNodes(node, "Patches/Patch")
            self.patches = [PatchInfo(p) for p in patchElts]
            buildDepElts = getAllNodes(node,
                                       "BuildDependencies/Dependency")
            self.buildDeps = [DepInfo(d) for d in buildDepElts]
            historyElts = getAllNodes(node, "History/Update")
            self.history = [UpdateInfo(x) for x in historyElts]
        
    def elt(self, xml):
        node = xml.newNode("Source")
        xml.addTextNodeUnder(node, "Name", self.name)
        if self.homepage:
            xml.addTextNodeUnder(node, "Homepage", self.homepage)
        node.appendChild(self.packager.elt(xml))
        xml.addTextNodeUnder(node, "Summary", self.summary)
        xml.addTextNodeUnder(node, "Description", self.description)
        if self.icon:
            xml.addTextNodeUnder(node, "Icon", self.icon)
        for lic in self.license:
            xml.addTextNodeUnder(node, "License", lic)
        for isa in self.isa:
            xml.addTextNodeUnder(node, "IsA", isa)
        xml.addTextNodeUnder(node, "PartOf", self.partof)
        archiveNode = xml.addNodeUnder(node, "Archive")
        archiveNode.setAttribute("type", self.archiveType)
        archiveNode.setAttribute("sha1sum", self.archiveSHA1)
        for patch in self.patches:
            xml.addNodeUnder(node, "Patches", patch.elt(xml))
        for dep in self.buildDeps:
            xml.addNodeUnder(node, "BuildDependencies", dep.elt(xml))
        for update in self.history:
            xml.addNodeUnder(node, "History", update.elt(xml))
        return node

    def has_errors(self):
        err = Checks()
        err.has_tag(self.name, "Source", "Name")
        err.has_tag(self.description, "Source", "Description")
        err.has_tag(self.summary, "Source", "Summary")
        err.has_tag(self.packager, "Source", "Packager")
        err.has_tag(self.license, "Source", "License")
        if (not self.archiveUri) or (not self.archiveType):
            err.add(_("Source archive URI and type should be given"))
        if not self.archiveSHA1:
            errd.add(_("Source archive should have a SHA1 sum"))
        if len(self.history) <= 0:
            err.add(_("Source needs some education in History :)"))
        
        err.join(self.packager.has_errors())
        for update in self.history:
            err.join(update.has_errors())
        for patch in self.patches:
            err.join(patch.has_errors())
        for dep in self.buildDeps:
            err.join(dep.has_errors())
        
        return err.list


class PackageInfo:
    """A structure to hold package information. Package information is
    located under <Package> tag in PSPEC file. Opposite to Source each
    PSPEC file can have more than one Package tag."""
    def __init__(self, node = None):
        if node:
            self.name = getNodeText(node, "Name")
            self.summary = getNodeText(node, "Summary")
            self.description = getNodeText(node, "Description")
            self.isa = map(getNodeText, getAllNodes(node, "IsA"))
            self.partof = getNodeText(node, "PartOf")
            self.license = map(getNodeText, getAllNodes(node, "License"))
            self.icon = getNodeText(node, "Icon")
            rtDepElts = getAllNodes(node, "RuntimeDependencies/Dependency")
            self.runtimeDeps = [DepInfo(x) for x in rtDepElts]
            self.paths = [PathInfo(x) for x in getAllNodes(node, "Files/Path")]
            historyElts = getAllNodes(node, "History/Update")
            self.history = [UpdateInfo(x) for x in historyElts]
            conflElts = getAllNodes(node, "Conflicts/Package")
            self.conflicts = map(getNodeText, conflElts)
            provComarElts = getAllNodes(node, "Provides/COMAR")
            self.providesComar = [ComarProvide(x) for x in provComarElts]
            reqComarElts = getAllNodes(node, "Requires/COMAR")
            self.requiresComar = map(getNodeText, reqComarElts)
            aFilesElts = getAllNodes(node, "AdditionalFiles/AdditionalFile")
            self.additionalFiles = [AdditionalFileInfo(f) for f in aFilesElts]

    def elt(self, xml):
        node = xml.newNode("Package")
        xml.addTextNodeUnder(node, "Name", self.name)
        xml.addTextNodeUnder(node, "Summary", self.summary)
        xml.addTextNodeUnder(node, "Description", self.description)
        if self.icon:
            xml.addTextNodeUnder(node, "Icon", self.icon)
        for lic in self.license:
            xml.addTextNodeUnder(node, "License", lic)
        for isa in self.isa:
            xml.addTextNodeUnder(node, "IsA", isa)
        if self.partof:
            xml.addTextNodeUnder(node, "PartOf", self.partof)
        for dep in self.runtimeDeps:
            xml.addNodeUnder(node, "RuntimeDependencies", dep.elt(xml))
        for path in self.paths:
            xml.addNodeUnder(node, "Files", path.elt(xml))
        for update in self.history:
            xml.addNodeUnder(node, "History", update.elt(xml))
        for conflict in self.conflicts:
            xml.addTextNodeUnder(node, "Conflicts/Package", conflict)
        for pcomar in self.providesComar:
            xml.addNodeUnder(node, "Provides", pcomar.elt(xml))
        for rcomar in self.requiresComar:
            xml.addTextNodeUnder(node, "Requires/COMAR", rcomar)
        for afile in self.additionalFiles:
            xml.addNodeUnder(node, "AdditionalFiles", afile.elt(xml))
        return node

    def has_errors(self):
        err = Checks()
        err.has_tag(self.name, "Package", "Name")
        err.has_tag(self.summary, "Package", "Summary")
        err.has_tag(self.description, "Package", "Description")
        err.has_tag(self.license, "Package", "License")
        if len(self.paths) <= 0:
            err.add(_("Package should have some files"))
        
        for path in self.paths:
            err.join(path.has_errors())
        for dep in self.runtimeDeps:
            err.join(dep.has_errors())
        for afile in self.additionalFiles:
            err.join(afile.has_errors())
        
        return err.list

    def __str__(self):
        s = _('Name: %s, version: %s, release: %s, build %s') % (
              self.name, self.version, self.release, self.build)
        s += _('\nSummary: ') + self.summary
        s += _('\nDescription: ') + self.description
        s += _('\nComponent: ') + self.partof
        s += _('\nProvides: ')
        for x in self.providesComar:
           s += x.om
        return s

    def pkg_dir(self):
        packageDir = self.name + '-' \
                     + self.version + '-' \
                     + self.release

        return join( config.lib_dir(), packageDir)

class SpecFile(XmlFile):
    """A class for reading/writing from/to a PSPEC (PISI SPEC) file."""

    def __init__(self):
        XmlFile.__init__(self,"PISI")

    def read(self, filename):
        """Read PSPEC file"""
        
        self.readxml(filename)

        self.source = SourceInfo(self.getNode("Source"))

        # As we have no Source/Version tag we need to get 
        # the last version and release information
        # from the first child of History/Update. And it works :)
        self.source.version = self.source.history[0].version
        self.source.release = self.source.history[0].release

        # find all binary packages
        packageElts = self.getAllNodes("Package")
        self.packages = [PackageInfo(p) for p in packageElts]

        self.merge_tags()
        self.override_tags()

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
        return err.list
    
    def write(self, filename):
        """Write PSPEC file"""
        self.newDOM()
        self.addChild(self.source.elt(self))
        for pkg in self.packages:
            self.addChild(pkg.elt(self))
        self.writexml(filename)
