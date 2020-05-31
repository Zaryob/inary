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
 Specfile module is our handler for PSPEC files. PSPEC (INARY SPEC)
 files are specification files for INARY source packages. This module
 provides read and write routines for PSPEC files.
"""

# Standart Python Modules
import os.path

# Inary Modules
import inary.db
import inary.errors
import inary.util as util
import inary.data.group as group
import inary.data.component as component
import inary.analyzer.conflict
import inary.data.replace
import inary.analyzer.dependency
import inary.context as ctx

# AutoXML Library
import inary.sxml.autoxml as autoxml
import inary.sxml.xmlext as xmlext
import inary.sxml.xmlfile as xmlfile

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class Error(inary.errors.Error):
    pass


class Packager(metaclass=autoxml.autoxml):
    t_Name = [autoxml.String, autoxml.mandatory]
    t_Email = [autoxml.String, autoxml.mandatory]

    def __str__(self):
        s = "{} <{}>".format(self.name, self.email)
        return s


class AdditionalFile(metaclass=autoxml.autoxml):
    s_Filename = [autoxml.String, autoxml.mandatory]
    a_target = [autoxml.String, autoxml.mandatory]
    a_permission = [autoxml.String, autoxml.optional]
    a_owner = [autoxml.String, autoxml.optional]
    a_group = [autoxml.String, autoxml.optional]

    def __str__(self):
        s = "{0} -> {1} ".format(self.filename, self.target)
        if self.permission:
            s += '({})'.format(self.permission)
        return s


class Type(metaclass=autoxml.autoxml):
    s_type = [autoxml.String, autoxml.mandatory]
    a_package = [autoxml.String, autoxml.optional]


class Action(metaclass=autoxml.autoxml):
    # Valid actions:
    #
    # reverseDependencyUpdate
    # systemRestart
    # serviceRestart

    s_action = [autoxml.String, autoxml.mandatory]
    a_package = [autoxml.String, autoxml.optional]
    a_target = [autoxml.String, autoxml.optional]

    def __str__(self):
        return self.action


class Patch(metaclass=autoxml.autoxml):
    s_Filename = [autoxml.String, autoxml.mandatory]
    a_compressionType = [autoxml.String, autoxml.optional]
    a_level = [autoxml.Integer, autoxml.optional]
    a_reverse = [autoxml.String, autoxml.optional]

    # FIXME: what's the cleanest way to give a default value for reading level?
    # def decode_hook(self, node, errs, where):
    #    if self.level == None:
    #        self.level = 0

    def __str__(self):
        s = self.filename
        if self.compressionType:
            s += ' (' + self.compressionType + ')'
        if self.level:
            s += ' level:' + self.level
        return s


class Update(metaclass=autoxml.autoxml):
    a_release = [autoxml.String, autoxml.mandatory]
    # 'type' attribute is here to keep backward compatibility
    a_type = [autoxml.String, autoxml.optional]
    t_types = [[Type], autoxml.optional, "Type"]
    t_Date = [autoxml.String, autoxml.mandatory]
    t_Version = [autoxml.String, autoxml.mandatory]
    t_Comment = [autoxml.String, autoxml.optional]
    t_Name = [autoxml.String, autoxml.optional]
    t_Email = [autoxml.String, autoxml.optional]
    t_Requires = [[Action], autoxml.optional]

    def __str__(self):
        s = self.date
        s += ", ver=" + self.version
        s += ", rel=" + self.release
        if self.type:
            s += ", type=" + self.type
        return s


class Path(metaclass=autoxml.autoxml):
    s_Path = [autoxml.String, autoxml.mandatory]
    a_fileType = [autoxml.String, autoxml.optional]
    a_permanent = [autoxml.String, autoxml.optional]
    a_replace = [autoxml.String, autoxml.optional]

    def __str__(self):
        s = self.path
        s += ", type=" + self.fileType
        return s


class ServiceProvide(metaclass=autoxml.autoxml):
    s_om = [autoxml.String, autoxml.mandatory]
    a_runlevel = [autoxml.String, autoxml.optional]

    def __str__(self):
        # FIXME: descriptive enough?
        s = self.om
        s += ' ( ' + self.runlevel + ' )'
        return s


class Archive(metaclass=autoxml.autoxml):
    s_uri = [autoxml.String, autoxml.mandatory]
    a_type = [autoxml.String, autoxml.optional]
    a_sha1sum = [autoxml.String, autoxml.mandatory]
    a_target = [autoxml.String, autoxml.optional]

    def decode_hook(self, node, errs, where):
        self.name = os.path.basename(str(self.uri))

    def __str__(self):
        s = _('URI: {0}, type: {1}, sha1sum: {2}').format(
            self.uri, self.type, self.sha1sum)
        return s


class Source(metaclass=autoxml.autoxml):
    t_Name = [autoxml.String, autoxml.mandatory]
    t_Homepage = [autoxml.String, autoxml.optional]
    t_Packager = [Packager, autoxml.mandatory]
    t_Rfp = [autoxml.String, autoxml.optional]
    t_ExcludeArch = [[autoxml.String], autoxml.optional]
    t_License = [[autoxml.String], autoxml.mandatory]
    t_IsA = [[autoxml.String], autoxml.optional]
    t_PartOf = [autoxml.String, autoxml.optional]
    t_Summary = [autoxml.LocalText, autoxml.mandatory]
    t_Description = [autoxml.LocalText, autoxml.mandatory]
    t_Icon = [autoxml.String, autoxml.optional]
    t_Archive = [[Archive], autoxml.mandatory, "Archive"]
    t_AdditionalFiles = [[AdditionalFile], autoxml.optional]
    t_BuildDependencies = [
        [inary.analyzer.dependency.Dependency], autoxml.optional]
    t_Patches = [[Patch], autoxml.optional]
    t_Version = [autoxml.String, autoxml.optional]
    t_Release = [autoxml.String, autoxml.optional]
    t_SourceURI = [autoxml.String, autoxml.optional]  # used in index

    def buildtimeDependencies(self):
        return self.buildDependencies


class AnyDependency(metaclass=autoxml.autoxml):
    t_Dependencies = [[inary.analyzer.dependency.Dependency],
                      autoxml.optional, "Dependency"]

    def __str__(self):
        return "{{}}".format(_(" or ").join(
            [str(dep) for dep in self.dependencies]))

    def name(self):
        return "{{}}".format(_(" or ").join(
            [dep.package for dep in self.dependencies]))

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


class Package(metaclass=autoxml.autoxml):
    t_Name = [autoxml.String, autoxml.mandatory]
    t_Summary = [autoxml.LocalText, autoxml.optional]
    t_Description = [autoxml.LocalText, autoxml.optional]
    t_IsA = [[autoxml.String], autoxml.optional]
    t_PartOf = [autoxml.String, autoxml.optional]
    t_License = [[autoxml.String], autoxml.optional]
    t_Icon = [autoxml.String, autoxml.optional]
    t_BuildFlags = [[autoxml.String], autoxml.optional, "BuildFlags/Flag"]
    t_BuildType = [autoxml.String, autoxml.optional]
    t_BuildDependencies = [
        [inary.analyzer.dependency.Dependency], autoxml.optional]
    t_PackageDependencies = [[inary.analyzer.dependency.Dependency],
                             autoxml.optional, "RuntimeDependencies/Dependency"]
    t_PackageAnyDependencies = [
        [AnyDependency],
        autoxml.optional,
        "RuntimeDependencies/AnyDependency"]
    t_ComponentDependencies = [[autoxml.String],
                               autoxml.optional, "RuntimeDependencies/Component"]
    t_Files = [[Path], autoxml.optional]
    t_Conflicts = [[inary.analyzer.conflict.Conflict],
                   autoxml.optional, "Conflicts/Package"]
    t_Replaces = [[inary.data.replace.Replace],
                  autoxml.optional, "Replaces/Package"]
    t_ProvidesCommand = [[autoxml.String],
                         autoxml.optional, "Provides/Command"]
    t_ProvidesCMAKE = [[autoxml.String], autoxml.optional, "Provides/CMAKE"]
    t_ProvidesPkgConfig = [[autoxml.String],
                           autoxml.optional, "Provides/PkgConfig"]
    t_ProvidesSharedObject = [[autoxml.String],
                              autoxml.optional, "Provides/SharedObject"]
    t_ProvidesService = [
        [ServiceProvide],
        autoxml.optional,
        "Provides/Service"]
    t_AdditionalFiles = [[AdditionalFile], autoxml.optional]
    t_History = [[Update], autoxml.optional]

    # FIXME: needed in build process, to distinguish dynamically generated debug packages.
    # find a better way to do this.
    debug_package = False

    def runtimeDependencies(self):
        componentdb = inary.db.componentdb.ComponentDB()
        deps = self.packageDependencies + self.packageAnyDependencies

        # Create Dependency objects for each package coming from
        # a component dependency.
        for componentName in self.componentDependencies:
            for pkgName in componentdb.get_component(componentName).packages:
                deps.append(
                    inary.analyzer.dependency.Dependency(
                        package=pkgName))

        return deps

    def pkg_dir(self):
        packageDir = self.name + '-' \
            + self.version + '-' \
            + self.release

        return util.join_path(ctx.config.packages_dir(), packageDir)

    def satisfies_runtime_dependencies(self):
        for dep in self.runtimeDependencies():
            if not dep.satisfied_by_installed():
                ctx.ui.error(
                    _('\"{0}\" dependency of package \"{1}\" is not satisfied.').format(
                        dep, self.name))
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
            installdb = inary.db.installdb.InstallDB()
            if not installdb.has_package(self.name):
                return {}

            old_release = installdb.get_release(self.name)

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
        s = _('Name: {0}, version: {1}, release: {2}\n').format(
            self.name, self.version, self.release)
        s += _('Summary: {}\n').format(str(self.summary))
        s += _('Description: {}\n').format(str(self.description))
        s += _('Licenses: {}\n').format(", ".join(self.license))
        s += _('Component: {}\n').format(str(self.partOf))
        s += _('Provides: \n')

        if(self.providesCommand):
            s += _('   - Commands: \n')
            for x in self.providesCommand:
                s += '       * {}\n'.format(x)

        if(self.providesCMAKE):
            s += _('   - CMAKE Needs: \n')
            for x in self.providesCMAKE:
                s += '       * {}\n'.format(x)

        if(self.providesPkgConfig):
            s += _('   - PkgConfig Needs: \n')
            for x in self.providesPkgConfig:
                s += '       * {}\n'.format(x)

        if(self.providesService):
            s += _('   - Services: \n')
            for x in self.providesService:
                s += '       * {}\n'.format(x)

        s += '\n'
        s += _('Dependencies: ')
        for x in self.componentDependencies:
            s += x + ' '
        for x in self.packageDependencies:
            s += x.name() + ' '
        for x in self.packageAnyDependencies:
            s += x.name() + ' '
        return s + '\n'


class SpecFile(xmlfile.XmlFile, metaclass=autoxml.autoxml):
    tag = "INARY"

    t_Source = [Source, autoxml.mandatory]
    t_Packages = [[Package], autoxml.mandatory, "Package"]
    t_History = [[Update], autoxml.mandatory]
    t_Components = [[component.Component], autoxml.optional, "Component"]
    t_Groups = [[group.Group], autoxml.optional, "Group"]

    def decode_hook(self, node, errs, where):
        current_version = self.history[0].version
        current_release = self.history[0].release

        for package in self.packages:
            deps = package.packageDependencies[:]
            deps += sum([x.dependencies for x
                         in package.packageAnyDependencies], [])
            for dep in deps:
                for attr_name, attr_value in list(dep.__dict__.items()):
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

    @staticmethod
    def _set_i18n(tag, inst):
        try:
            for summary in xmlext.getTagByName(tag, "Summary"):
                inst.summary[xmlext.getNodeAttribute(
                    summary, "xml:lang")] = xmlext.getNodeText(summary)
            for desc in xmlext.getTagByName(tag, "Description"):
                inst.description[xmlext.getNodeAttribute(
                    desc, "xml:lang")] = xmlext.getNodeText(desc)
        except AttributeError as e:
            raise Error(
                _("translations.xml file is badly formed.: {}").format(e))

    def read_translations(self, path):
        if not os.path.exists(path):
            return

        doc = xmlext.parse(path)

        if xmlext.getNodeText(xmlext.getNode(doc, "Source"),
                              "Name") == self.source.name:
            # Set source package translations
            self._set_i18n(xmlext.getNode(doc, "Source"), self.source)

        for pak in xmlext.getTagByName(doc, "Package"):
            for inst in self.packages:
                if inst.name == xmlext.getNodeText(pak, "Name"):
                    self._set_i18n(pak, inst)
                    break

    def __str__(self):
        s = _('Name: {0}, version: {1}, release: {2}\n').format(
            self.source.name, self.history[0].version, self.history[0].release)
        s += _('Summary: {}\n').format(str(self.source.summary))
        s += _('Description: {}\n').format(str(self.source.description))
        s += _('Licenses: {}\n').format(", ".join(self.source.license))
        s += _('Component: {}\n').format(str(self.source.partOf))
        s += _('Build Dependencies: ')
        for x in self.source.buildDependencies:
            s += x.package + ' '
        return s
