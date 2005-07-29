# -*- coding: utf-8 -*-

# Specfile module is our handler for PSPEC files. PSPEC (PISI SPEC)
# files are specification files for PISI source packages. This module
# provides read and write access to PSPEC files.

# Authors:  Eray Ozkural <eray@uludag.org.tr>
#           Baris Metin <baris@uludag.org.tr

# standard python modules
from os.path import basename

# pisi modules
from xmlext import *
from xmlfile import XmlFile
from ui import ui

class PackagerInfo:
    def __init__(self, node = None):
        if node:
            self.name = getNodeText(getNode(node, "Name"))
            self.email = getNodeText(getNode(node, "Email"))

    def elt(self, xml):
        node = xml.newNode("Packager")
        xml.addTextNodeUnder(node, "Name", self.name)
        xml.addTextNodeUnder(node, "Email", self.email)
        return node

    def verify(self):
        if not self.name: return False
        if not self.email: return False
        return True

class AdditionalFileInfo:
    def __init__(self, node = None):
        if node:
            self.filename = getNodeText(node)
            self.target = getNodeAttribute(node, "target")
            self.permission = getNodeAttribute(node, "permission")
            self.owner = getNodeAttribute(node, "owner")
        else:
            self.permission = self.owner = None

    def elt(self, xml):
        node = xml.newNode("AdditionalFile")
        xml.addText(node, self.filename)
        node.setAttribute("target", self.target)
        if self.permission:
            node.setAttribute("permission", self.permission)
        if self.owner:
            node.setAttribute("owner", self.owner)

    def verify(self):
        if not self.filename: return False
        if not self.target: return False
        return True

class PatchInfo:
    def __init__(self, node = None):
        if node:
            self.filename = getNodeText(node)
            self.compressionType = getNodeAttribute(node, "compressionType")
            self.level = getNodeAttribute(node, "level")
        else:
            self.compressionType = None
        if not self.level:
            self.level = 0
        else:
            self.level = int(self.level)

    def elt(self, xml):
        node = xml.newNode("Patch")
        xml.addText(node, self.filename)
        if self.compressionType:
            node.setAttribute("compressionType", self.compressionType)
        if self.level:
            node.setAttribute("level", str(self.level))
        return node

    def verify(self):
        if not self.filename: return False
        return True

class DepInfo:
    def __init__(self, node = None):
        if node:
            self.package = getNodeText(node).strip()
            self.versionFrom = getNodeAttribute(node, "versionFrom")
            self.versionTo = getNodeAttribute(node, "versionTo")
            self.releaseFrom = getNodeAttribute(node, "releaseFrom")
            self.releaseTo = getNodeAttribute(node, "releaseTo")
        else:
            self.versionFrom = self.versionTo = None
            self.releaseFrom = self.releaseFrom = None

    def elt(self, xml):
        node = xml.newNode("Dependency")
        xml.addText(node, self.package)
        if self.versionFrom:
            node.setAttribute("versionFrom", self.versionFrom)
        if self.versionTo:
            node.setAttribute("versionTo", self.versionTo)
        if self.releaseFrom:
            node.setAttribute("releaseFrom", self.versionFrom)
        if self.releaseTo:
            node.setAttribute("releaseTo", self.versionTo)
        return node

    def verify(self):
        if not self.package: return False
        return True

    def satisfies(self, pkg_name, version, release):
        """determine if a package ver. satisfies given dependency spec"""
        ret = True
        from version import Version
        if self.versionFrom:
            ret &= Version(version) >= Version(depinfo.versionFrom)
        if self.versionTo:
            ret &= Version(version) <= Version(depinfo.versionTo)        
        if self.releaseFrom:
            ret &= Version(release) <= Version(depinfo.releaseFrom)        
        if self.releaseTo:
            ret &= Version(release) <= Version(depinfo.releaseTo)       
        return ret
        
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

    def verify(self):
        if not self.date: return False
        if not self.version: return False
        if not self.release: return False
        return True

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

    def verify(self):
        if not self.pathname: return False
        return True

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

    def verify(self):
        if not self.om or not self.script:
            return False
        return True

class SourceInfo:
    """A structure to hold source information. Source information is
    located under <Source> tag in PSPEC file."""
    def __init__(self, node = None):
        if node:
            self.name = getNodeText(node, "Name")
            self.homepage = getNodeText(node, "HomePage")
            self.packager = PackagerInfo(getNode(node, "Packager"))
            self.summary = getNodeText(node, "Summary")
            self.description = getNodeText(node, "Description")
            self.license = map(getNodeText, getAllNodes(node, "License"))
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
        xml.addTextNodeUnder(node, "Description", self.description)
        for l in self.license:
            xml.addTextNodeUnder(node, "License", l)
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

    def verify(self):
        if not self.name: return False
        if not self.summary: return False
        if not self.description: return False
        if not self.packager: return False
        if not self.license: return False
        if (not self.archiveUri) or (not self.archiveType): return False
        if not self.archiveSHA1: return False
        if len(self.history) <= 0: return False
        
        if not self.packager.verify(): return False
        for update in self.history:
            if not update.verify(): return False
        for patch in self.patches:
            if not patch.verify(): return False
        for dep in self.buildDeps:
            if not dep.verify(): return False

        return True

class PackageInfo(object):
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
        for l in self.license:
            xml.addTextNodeUnder(node, "License", l)
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

    def verify(self):
        if not self.name: return False
        if not self.summary: return False
        if not self.description: return False
        if not self.license: return False
        if len(self.paths) <= 0: return False

        for path in self.paths:
            if not path.verify(): return False
        for dep in self.runtimeDeps:
            if not dep.verify(): return False
        for afile in self.additionalFiles:
            if not afile.verify(): return False
        return True

    def __str__(self):
        s = 'Name: ' + self.name
        s += '\nSummary: ' + self.summary
        s += '\nDescription: ' + self.description
        return s

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

        self.doMerges()
        self.doOverrides()

        self.unlink()

    def doOverrides(self):
        """Override tags from Source in Packages. Some tags in Packages
        overrides the tags from Source. There is a more detailed
        description in documents."""

        for pkg in self.packages:

            if not pkg.summary:
                pkg.summary = self.source.summary

            if not pkg.description:
                pkg.description = self.source.description

            if not pkg.partof:
                pkg.partof = self.source.partof

            if not pkg.license:
                pkg.license = self.source.license
        
    def doMerges(self):
        """Merge tags from Source in Packages. Some tags in Packages merged
        with the tags from Source. There is a more detailed
        description in documents."""

        for pkg in self.packages:

            if pkg.isa and self.source.isa:
                pkg.isa.append(self.source.isa)
            elif not pkg.isa and self.source.isa:
                pkg.isa = self.source.isa

        
    def verify(self):
        """Verify PSPEC structures, are they what we want of them?"""
        if not self.source.verify(): return False
        if len(self.packages) <= 0: return False
        for x in self.packages:
            if not x.verify(): return False
        return True
    
    def write(self, filename):
        """Write PSPEC file"""
        self.newDOM()
        self.addChild(self.source.elt(self))
        for pkg in self.packages:
            self.addChild(pkg.elt(self))
        self.writexml(filename)
