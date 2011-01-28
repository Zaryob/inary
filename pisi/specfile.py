# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2010, TUBITAK/UEKAE
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
import pisi.group as group
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

class Type:

    s_type = [autoxml.String, autoxml.mandatory]
    a_package = [autoxml.String, autoxml.optional]

class Action:

    # Valid actions:
    #
    # reverseDependencyUpdate
    # systemRestart
    # serviceRestart

    s_action  = [autoxml.String, autoxml.mandatory]
    a_package = [autoxml.String, autoxml.optional]
    a_target  = [autoxml.String, autoxml.optional]

    def __str__(self):
        return self.action

class Patch:

    s_Filename = [autoxml.String, autoxml.mandatory]
    a_compressionType = [autoxml.String, autoxml.optional]
    a_level = [autoxml.Integer, autoxml.optional]
    a_reverse = [autoxml.String, autoxml.optional]

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

class Update:

    a_release = [autoxml.String, autoxml.mandatory]
    # 'type' attribute is here to keep backward compatibility
    a_type = [autoxml.String, autoxml.optional]
    t_types = [[Type], autoxml.optional, "Type"]
    t_Date = [autoxml.String, autoxml.mandatory]
    t_Version = [autoxml.String, autoxml.mandatory]
    t_Comment = [autoxml.String, autoxml.optional]
    t_Name = [autoxml.Text, autoxml.optional]
    t_Email = [autoxml.String, autoxml.optional]
    t_Requires = [[Action], autoxml.optional]

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
    a_name = [autoxml.String, autoxml.optional]

    def __str__(self):
        # FIXME: descriptive enough?
        s = self.script
        s += ' (' + self.om + '%s' % (' for %s' % self.name if self.name else '') + ')'
        return s

class Archive:

    s_uri = [ autoxml.String, autoxml.mandatory ]
    a_type = [ autoxml.String, autoxml.optional ]
    a_sha1sum =[ autoxml.String, autoxml.mandatory ]
    a_target =[ autoxml.String, autoxml.optional ]

    def decode_hook(self, node, errs, where):
        self.name = os.path.basename(self.uri)

    def __str__(self):
        s = _('URI: %s, type: %s, sha1sum: %s') % (self.uri, self.type, self.sha1sum)
        return s

class Source:

    t_Name = [autoxml.String, autoxml.mandatory]
    t_Homepage = [autoxml.String, autoxml.optional]
    t_Packager = [Packager, autoxml.mandatory]
    t_ExcludeArch = [ [autoxml.String], autoxml.optional]
    t_License = [ [autoxml.String], autoxml.mandatory]
    t_IsA = [ [autoxml.String], autoxml.optional]
    t_PartOf = [autoxml.String, autoxml.optional]
    t_Summary = [autoxml.LocalText, autoxml.mandatory]
    t_Description = [autoxml.LocalText, autoxml.mandatory]
    t_Icon = [ autoxml.String, autoxml.optional]
    t_Archive = [ [Archive], autoxml.mandatory, "Archive" ]
    t_AdditionalFiles = [ [AdditionalFile], autoxml.optional]
    t_BuildDependencies = [ [pisi.dependency.Dependency], autoxml.optional]
    t_Patches = [ [Patch], autoxml.optional]
    t_Version = [ autoxml.String, autoxml.optional]
    t_Release = [ autoxml.String, autoxml.optional]
    t_SourceURI = [ autoxml.String, autoxml.optional ] # used in index

    def buildtimeDependencies(self):
        return self.buildDependencies

class AnyDependency:
    t_Dependencies = [[pisi.dependency.Dependency], autoxml.optional, "Dependency"]

    def __str__(self):
        return "{%s}" % _(" or ").join([str(dep) for dep in self.dependencies])

    def name(self):
        return "{%s}" % _(" or ").join([dep.package for dep in self.dependencies])

    def decode_hook(self, node, errs, where):
        self.package = self.dependencies[0].package

    def satisfied_by_dict_repo(self, dict_repo):
        for dependency in self.dependencies:
            if dependency.satisfied_by_dict_repo(dict_repo):
                return True
        return False

    def satisfied_by_any_installed_other_than(self, package):
        for dependency in self.dependencies:
            if dependency.package != package and dependency.satisfied_by_installed():
                return True
        return False

    def satisfied_by_installed(self):
        for dependency in self.dependencies:
            if dependency.satisfied_by_installed():
                return True
        return False

    def satisfied_by_repo(self):
        for dependency in self.dependencies:
            if dependency.satisfied_by_repo():
                return True
        return False

class Package:

    t_Name = [ autoxml.String, autoxml.mandatory ]
    t_Summary = [ autoxml.LocalText, autoxml.optional ]
    t_Description = [ autoxml.LocalText, autoxml.optional ]
    t_IsA = [ [autoxml.String], autoxml.optional]
    t_PartOf = [autoxml.String, autoxml.optional]
    t_License = [ [autoxml.String], autoxml.optional]
    t_Icon = [ autoxml.String, autoxml.optional]
    t_PackageDependencies = [ [pisi.dependency.Dependency], autoxml.optional, "RuntimeDependencies/Dependency"]
    t_PackageAnyDependencies = [[AnyDependency], autoxml.optional, "RuntimeDependencies/AnyDependency"]
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
        deps = self.packageDependencies + self.packageAnyDependencies
        deps += [ componentdb.get_component(x).packages for x in self.componentDependencies ]
        return deps

    def pkg_dir(self):
        packageDir = self.name + '-' \
                     + self.version + '-' \
                     + self.release

        return util.join_path(ctx.config.packages_dir(), packageDir)

    def satisfies_runtime_dependencies(self):
        for dep in self.runtimeDependencies():
            if not dep.satisfied_by_installed():
                ctx.ui.error(_('%s dependency of package %s is not satisfied') % (dep, self.name))
                return False
        return True

    def installable(self):
        """calculate if pkg is installable currently"""
        return self.satisfies_runtime_dependencies()

    def get_update_types(self, old_release):
        """Returns update types for the releases greater than old_release.

        @type  old_release: string
        @param old_release: The release of the installed package.

        @rtype:  set of strings
        @return: Update types.
        """

        types = set()

        for update in self.history:
            if update.release == old_release:
                break

            if update.type:
                types.add(update.type)

            for type_ in update.types:
                if type_.package and type_.package != self.name:
                    continue

                types.add(type_.type)

        return types

    def has_update_type(self, type_name, old_release):
        """Checks whether the package has the given update type.

        @type  type_name:   string
        @param type_name:   Name of the update type.
        @type  old_release: string
        @param old_release: The release of the installed package.

        @rtype:  bool
        @return: True if the type exists, else False.
        """

        for update in self.history:
            if update.release == old_release:
                break

            if update.type == type_name:
                return True

            for type_ in update.types:
                if type_.package and type_.package != self.name:
                    continue

                if type_.type == type_name:
                    return True

        return False

    def get_update_actions(self, old_release=None):
        """Returns update actions for the releases greater than old_release.

        @type  old_release: string
        @param old_release: The release of the installed package.

        @rtype:  dict
        @return: A set of affected packages for each action.
        """

        if old_release is None:
            installdb = pisi.db.installdb.InstallDB()
            if not installdb.has_package(self.name):
                return {}

            version, old_release, build = installdb.get_version(self.name)

        actions = {}

        for update in self.history:
            if update.release == old_release:
                break

            for action in update.requires:
                if action.package and action.package != self.name:
                    continue

                target = action.target or self.name
                actions.setdefault(action.action, set()).add(target)

        return actions

    def __str__(self):
        s = _('Name: %s, version: %s, release: %s\n') \
                % (self.name, self.version, self.release)
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
           s += x.name() + ' '
        for x in self.packageAnyDependencies:
           s += x.name() + ' '
        return s + '\n'


class SpecFile(xmlfile.XmlFile):
    __metaclass__ = autoxml.autoxml #needed when we specify a superclass

    tag = "PISI"

    t_Source = [ Source, autoxml.mandatory]
    t_Packages = [ [Package], autoxml.mandatory, "Package"]
    t_History = [ [Update], autoxml.mandatory]
    t_Components = [ [component.Component], autoxml.optional, "Component"]
    t_Groups = [ [group.Group], autoxml.optional, "Group"]

    def decode_hook(self, node, errs, where):
        current_version = self.history[0].version
        current_release = self.history[0].release

        for package in self.packages:
            deps = package.packageDependencies[:]
            deps += sum([x.dependencies for x
                         in package.packageAnyDependencies], [])
            for dep in deps:
                for attr_name, attr_value in dep.__dict__.items():
                    if attr_value != "current":
                        continue

                    if attr_name.startswith("version"):
                        dep.__dict__[attr_name] = current_version

                    elif attr_name.startswith("release"):
                        dep.__dict__[attr_name] = current_release


    def getSourceVersion(self):
        return self.history[0].version

    def getSourceRelease(self):
        return self.history[0].release

    def _set_i18n(self, tag, inst):
        try:
            for summary in tag.tags("Summary"):
                inst.summary[summary.getAttribute("xml:lang")] = summary.firstChild().data()
            for desc in tag.tags("Description"):
                inst.description[desc.getAttribute("xml:lang")] = desc.firstChild().data()
        except AttributeError:
            raise Error(_("translations.xml file is badly formed."))


    def read_translations(self, path):
        if not os.path.exists(path):
            return
        try:
            doc = piksemel.parse(path)
        except Exception, e:
            raise Error(_("File '%s' has invalid XML") % (path) )

        if doc.getTag("Source").getTagData("Name") == self.source.name:
            # Set source package translations
            self._set_i18n(doc.getTag("Source"), self.source)

        for pak in doc.tags("Package"):
            for inst in self.packages:
                if inst.name == pak.getTagData("Name"):
                    self._set_i18n(pak, inst)
                    break

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
