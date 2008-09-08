# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 - 2007, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

"""
 Specfile module is our handler for PSPEC files. PSPEC (PiSi SPEC)
 files are specification files for PiSi source packages. This module
 provides read and write routines for PSPEC files.
"""

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

# standard python modules
import os.path
import piksemel

# pisi modules
import pisi.pxml.xmlfile as xmlfile
import pisi.pxml.autoxml as autoxml
import pisi.context as ctx
import pisi.dependency
import pisi.replace
import pisi.conflict
import pisi.component as component
import pisi.util as util
import pisi.db

class Error(pisi.Error):
    pass

__metaclass__ = autoxml.autoxml

class Packager:

    t_Name = [autoxml.Text, autoxml.mandatory]
    t_Email = [autoxml.String, autoxml.mandatory]

    def __str__(self):
        s = "%s <%s>" % (self.name, self.email)
        return s


class AdditionalFile:

    s_Filename = [autoxml.String, autoxml.mandatory]
    a_target = [autoxml.String, autoxml.mandatory]
    a_permission = [autoxml.String, autoxml.optional]
    a_owner = [autoxml.String, autoxml.optional]
    a_group = [autoxml.String, autoxml.optional]

    def __str__(self):
        s = "%s -> %s " % (self.filename, self.target)
        if self.permission:
            s += '(%s)' % self.permission
        return s

class Patch:

    s_Filename = [autoxml.String, autoxml.mandatory]
    a_compressionType = [autoxml.String, autoxml.optional]
    a_level = [autoxml.Integer, autoxml.optional]

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
        return s

class Requires:

    # Valid actions:
    #
    # reverseDependencyUpdate
    # systemRestart
    # serviceRestart

    t_Action = [ [autoxml.String], autoxml.mandatory]

class Update:

    a_release = [autoxml.String, autoxml.mandatory]
    a_type = [autoxml.String, autoxml.optional]
    t_Date = [autoxml.String, autoxml.mandatory]
    t_Version = [autoxml.String, autoxml.mandatory]
    t_Comment = [autoxml.String, autoxml.optional]
    t_Name = [autoxml.Text, autoxml.optional]
    t_Email = [autoxml.String, autoxml.optional]
    t_Requires = [Requires, autoxml.optional]

    def __str__(self):
        s = self.date
        s += ", ver=" + self.version
        s += ", rel=" + self.release
        if self.type:
            s += ", type=" + self.type
        return s

class Path:

    s_Path = [autoxml.String, autoxml.mandatory]
    a_fileType =  [autoxml.String, autoxml.optional]
    a_permanent =  [autoxml.String, autoxml.optional]

    def __str__(self):
        s = self.path
        s += ", type=" + self.fileType
        return s


class ComarProvide:

    s_om = [autoxml.String, autoxml.mandatory]
    a_script = [autoxml.String, autoxml.mandatory]

    def __str__(self):
        # FIXME: descriptive enough?
        s = self.script
        s += ' (' + self.om + ')'
        return s

class Archive:

    s_uri = [ autoxml.String, autoxml.mandatory ]
    a_type =[ autoxml.String, autoxml.mandatory ]
    a_sha1sum =[ autoxml.String, autoxml.mandatory ]

    def decode_hook(self, node, errs, where):
        self.name = os.path.basename(self.uri)

    def __str__(self):
        s = _('URI: %s, type: %s, sha1sum: %s') % (self.uri, self.type, self.sha1sum)
        return s


class Source:

    t_Name = [autoxml.String, autoxml.mandatory]
    t_Homepage = [autoxml.String, autoxml.optional]
    t_Packager = [Packager, autoxml.mandatory]
    t_License = [ [autoxml.String], autoxml.mandatory]
    t_IsA = [ [autoxml.String], autoxml.optional]
    t_PartOf = [autoxml.String, autoxml.optional]
    t_Summary = [autoxml.LocalText, autoxml.mandatory]
    t_Description = [autoxml.LocalText, autoxml.optional]
    t_Icon = [ autoxml.String, autoxml.optional]
    t_Archive = [Archive, autoxml.mandatory ]
    t_BuildDependencies = [ [pisi.dependency.Dependency], autoxml.optional]
    t_Patches = [ [Patch], autoxml.optional]
    t_Version = [ autoxml.String, autoxml.optional]
    t_Release = [ autoxml.String, autoxml.optional]
    t_SourceURI = [ autoxml.String, autoxml.optional ] # used in index

class Package:

    t_Name = [ autoxml.String, autoxml.mandatory ]
    t_Summary = [ autoxml.LocalText, autoxml.optional ]
    t_Description = [ autoxml.LocalText, autoxml.optional ]
    t_IsA = [ [autoxml.String], autoxml.optional]
    t_PartOf = [autoxml.String, autoxml.optional]
    t_License = [ [autoxml.String], autoxml.optional]
    t_Icon = [ autoxml.String, autoxml.optional]
    t_PackageDependencies = [ [pisi.dependency.Dependency], autoxml.optional, "RuntimeDependencies/Dependency"]
    t_ComponentDependencies = [ [autoxml.String], autoxml.optional, "RuntimeDependencies/Component"]
    t_Files = [ [Path], autoxml.optional]
    t_Conflicts = [ [pisi.conflict.Conflict], autoxml.optional, "Conflicts/Package"]
    t_Replaces = [ [pisi.replace.Replace], autoxml.optional, "Replaces/Package"]
    t_ProvidesComar = [ [ComarProvide], autoxml.optional, "Provides/COMAR"]
    t_AdditionalFiles = [ [AdditionalFile], autoxml.optional]
    t_History = [ [Update], autoxml.optional]

    # FIXME: needed in build process, to distinguish dynamically generated debug packages.
    # find a better way to do this.
    debug_package = False

    def runtimeDependencies(self):
        componentdb = pisi.db.componentdb.ComponentDB()
        deps = self.packageDependencies
        deps += [ componentdb.get_component[x].packages for x in self.componentDependencies ]
        return deps

    def pkg_dir(self):
        packageDir = self.name + '-' \
                     + self.version + '-' \
                     + self.release

        return util.join_path(ctx.config.packages_dir(), packageDir)

    def installable(self):
        """calculate if pkg is installable currently"""
        deps = self.runtimeDependencies()
        return pisi.dependency.satisfies_dependencies(self.name, deps)

    def __str__(self):
        if self.build:
            build = self.build
        else:
            build = '--'
        s = _('Name: %s, version: %s, release: %s, build %s\n') % (
              self.name, self.version, self.release, build)
        s += _('Summary: %s\n') % unicode(self.summary)
        s += _('Description: %s\n') % unicode(self.description)
        s += _('Component: %s\n') % unicode(self.partOf)
        s += _('Provides: ')
        for x in self.providesComar:
           s += x.om + ' '
        s += '\n'
        s += _('Dependencies: ')
        for x in self.componentDependencies:
           s += x.package + ' '
        for x in self.packageDependencies:
           s += x.package + ' '
        return s + '\n'


class SpecFile(xmlfile.XmlFile):
    __metaclass__ = autoxml.autoxml #needed when we specify a superclass

    tag = "PISI"

    t_Source = [ Source, autoxml.mandatory]
    t_Packages = [ [Package], autoxml.mandatory, "Package"]
    t_History = [ [Update], autoxml.mandatory]
    t_Components = [ [component.Component], autoxml.optional, "Component"]

    def getSourceVersion(self):
        return self.history[0].version

    def getSourceRelease(self):
        return self.history[0].release

    def dirtyWorkAround(self):
        #TODO: Description should be mandatory. Remove this code when repo is ready.
        #http://liste.pardus.org.tr/gelistirici/2006-September/002332.html
        self.source.description = autoxml.LocalText("Description")
        self.source.description["en"] = self.source.summary["en"]

    def _set_i18n(self, tag, inst):
        for summary in tag.tags("Summary"):
            inst.summary[summary.getAttribute("xml:lang")] = summary.firstChild().data()
        for desc in tag.tags("Description"):
            inst.description[desc.getAttribute("xml:lang")] = desc.firstChild().data()

    def read_translations(self, path):
        if not os.path.exists(path):
            return
        doc = piksemel.parse(path)

        self._set_i18n(doc.getTag("Source"), self.source)
        for pak in doc.tags("Package"):
            for inst in self.packages:
                if inst.name == pak.getTagData("Name"):
                    break
            self._set_i18n(pak, inst)

    def __str__(self):
        s = _('Name: %s, version: %s, release: %s\n') % (
              self.source.name, self.history[0].version, self.history[0].release)
        s += _('Summary: %s\n') % unicode(self.source.summary)
        s += _('Description: %s\n') % unicode(self.source.description)
        s += _('Component: %s\n') % unicode(self.source.partOf)
        s += _('Build Dependencies: ')
        for x in self.source.buildDependencies:
           s += x.package + ' '
        return s
