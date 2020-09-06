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
#
# installation database
#


# Standart Python Modules
import os
import re

# Inary Modules
import inary.data
import inary.util
import inary.context as ctx
import inary.db.lazydb as lazydb
import inary.data.files as Files
import inary.analyzer.dependency

# AutoXML Library
from inary.sxml import xmlext, autoxml

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

# INARY


class InstallDBError(inary.errors.Error):
    pass


class CorruptedPackageError(inary.errors.Error):
    pass


class InstallInfo:
    state_map = {'i': _('installed'), 'ip': _('installed-pending')}

    def __init__(self, state, version, release, distribution, time):
        self.state = state
        self.version = version
        self.release = release
        self.distribution = distribution
        self.time = time

    def one_liner(self):
        import time
        time_str = time.strftime("%d %b %Y %H:%M", self.time)
        s = '%2s|%15s|%6s|%8s|%12s' % (self.state, self.version, self.release,
                                       self.distribution, time_str)
        return s

    def __str__(self):
        s = _("State: {0}\nVersion: {1}, Release: {2}\n").format(
            InstallInfo.state_map[self.state], self.version, self.release)
        import time
        time_str = time.strftime("%d %b %Y %H:%M", self.time)
        s += _('Distribution: {0}, Install Time: {1}\n').format(self.distribution,
                                                                time_str)
        return s


class InstallDB(lazydb.LazyDB):

    def __init__(self):
        lazydb.LazyDB.__init__(
            self,
            cacheable=True,
            cachedir=ctx.config.packages_dir())
        self.installed_db = self.__generate_installed_pkgs()

        # self.init()

    def init(self):
        self.__generate_inode_cache()  # TODO: Needs look it up.
        self.rev_deps_db = self.__generate_revdeps()
        self.installed_extra = self.__generate_installed_extra()

    def __generate_inode_cache(self):
        # This made to fix issue
        # https://stackoverflow.com/questions/26178038/python-slow-read-performance-issue
        # Clear old inode cache TODO: drop cache need option
        # open("/proc/sys/vm/drop_caches","w").write("2")
        for package in self.list_installed():
            ie_path = os.path.join(
                self.package_path(package),
                ctx.const.metadata_xml)
            ctx.ui.info(_("Checking package directory of \"{}\" package").format(
                package), verbose=True)
            if os.path.isfile(ie_path):
                fd = os.open(ie_path, os.O_RDONLY)
                itag = os.read(fd, 7)
                os.close(fd)

                if itag == b'<INARY>' or b'<?xml v':
                    pass
                else:
                    ctx.ui.warning(_("File content of metadata.xml can be corrupted.\n"
                                     "Probably filesystem crashed. \n"
                                     "Check your installation of \"{0}\" package and filesystem.").format(package))
                    raise CorruptedPackageError(
                        _("\"{}\" corrupted.").format(package))

            else:
                ctx.ui.warning(_("Unhandled corruption on \"{0}\" package metadata.\n"
                                 "There is not any metadata.xml file for {0} package.\n"
                                 "Please check installation of \"{0}\" package").format(package))
                raise CorruptedPackageError(
                    _("\"{}\" corrupted.").format(package))

    @staticmethod
    def __generate_installed_extra():
        ie = []
        ie_path = os.path.join(
            ctx.config.info_dir(),
            ctx.const.installed_extra)
        if os.path.isfile(ie_path):
            with open(ie_path) as ie_file:
                ie.extend(ie_file.read().strip().split("\n"))
        return ie

    @staticmethod
    def __generate_installed_pkgs():
        installed_list = []

        def split_name(dirname):
            name, version, release = dirname.rsplit("-", 2)
            installed_list.append((name, version + "-" + release))

        for i in os.listdir(ctx.config.packages_dir()):
            split_name(i)
        return dict(installed_list)

    @staticmethod
    def __get_marked_packages(_type):
        info_path = os.path.join(ctx.config.info_dir(), _type)
        if os.path.exists(info_path):
            return open(info_path).read().split()
        return []

    def __add_to_revdeps(self, package, revdeps):
        metadata_xml = os.path.join(
            self.package_path(package),
            ctx.const.metadata_xml)
        meta_doc = xmlext.parse(metadata_xml)

        try:
            pkg = xmlext.getNode(meta_doc, "Package")
        except BaseException:
            pkg = None

        if pkg is None:
            # If package info is broken or not available, skip it.
            ctx.ui.warning(_("Installation info for package \"{}\" is broken. "
                             "Reinstall it to fix this problem.").format(package))
            del self.installed_db[package]
            return

        deps = xmlext.getNode(pkg, 'RuntimeDependencies')
        if deps:
            for dep in xmlext.getTagByName(deps, 'Dependency'):
                revdep = revdeps.setdefault(xmlext.getNodeText(dep), {})
                revdep[package] = xmlext.toString(dep)

            for anydep in xmlext.getTagByName(deps, 'AnyDependency'):
                for dep in xmlext.getTagByName(anydep, 'Dependency'):
                    revdep = revdeps.setdefault(xmlext.getNodeText(dep), {})
                    revdep[package] = xmlext.toString(anydep)

    def __generate_revdeps(self):
        revdeps = {}
        for package in self.list_installed():
            self.__add_to_revdeps(package, revdeps)
        return revdeps

    def list_installed(self):
        return list(self.installed_db.keys())

    def has_package(self, package):
        return package in self.installed_db

    def list_installed_with_build_host(self, build_host):
        build_host_re = re.compile("<BuildHost>(.*?)</BuildHost>")
        found = []
        for name in self.list_installed():
            xml = open(
                os.path.join(
                    self.package_path(name),
                    ctx.const.metadata_xml)).read()
            matched = build_host_re.search(xml)
            if matched:
                if build_host != matched.groups()[0]:
                    continue
            elif build_host:
                continue

            found.append(name)

        return found

    @staticmethod
    def __get_summary(meta_doc):
        package = xmlext.getNode(meta_doc, 'Package')
        summary = xmlext.getNodeText(package, 'Summary')

        return summary

    @staticmethod
    def __get_version(meta_doc):
        package = xmlext.getNode(meta_doc, 'Package')
        history = xmlext.getNode(package, 'History')
        update = xmlext.getNode(history, 'Update')

        version = xmlext.getNodeText(update, 'Version')
        release = xmlext.getNodeAttribute(update, 'release')

        return version, release, None

    @staticmethod
    def __get_release(meta_doc):
        package = xmlext.getNode(meta_doc, 'Package')
        history = xmlext.getNode(package, 'History')
        update = xmlext.getNode(history, 'Update')
        return xmlext.getNodeAttribute(update, 'release')

    @staticmethod
    def __get_distro_release(meta_doc):
        package = xmlext.getNode(meta_doc, 'Package')
        distro = xmlext.getNodeText(package, 'Distribution')
        release = xmlext.getNodeText(package, 'DistributionRelease')

        return distro, release

    @staticmethod
    def __get_install_tar_hash(meta_doc):
        package = xmlext.getNode(meta_doc, 'Package')
        hash = xmlext.getNodeText(package, 'InstallTarHash')
        return hash

    def get_install_tar_hash(self, package):
        metadata_xml = os.path.join(
            self.package_path(package),
            ctx.const.metadata_xml)

        meta_doc = xmlext.parse(metadata_xml)

        return self.__get_install_tar_hash(meta_doc)

    def get_version_and_distro_release(self, package):
        metadata_xml = os.path.join(
            self.package_path(package),
            ctx.const.metadata_xml)

        meta_doc = xmlext.parse(metadata_xml)

        return self.__get_version(meta_doc) + \
            self.__get_distro_release(meta_doc)

    def get_distro_release(self, package):
        metadata_xml = os.path.join(
            self.package_path(package),
            ctx.const.metadata_xml)

        meta_doc = xmlext.parse(metadata_xml)

        return self.__get_distro_release(meta_doc)

    def get_version(self, package):
        metadata_xml = os.path.join(
            self.package_path(package),
            ctx.const.metadata_xml)

        meta_doc = xmlext.parse(metadata_xml)

        return self.__get_version(meta_doc)

    def get_release(self, package):
        metadata_xml = os.path.join(
            self.package_path(package),
            ctx.const.metadata_xml)

        meta_doc = xmlext.parse(metadata_xml)

        return self.__get_release(meta_doc)

    def get_summary(self, package):
        metadata_xml = os.path.join(
            self.package_path(package),
            ctx.const.metadata_xml)
        meta_doc = xmlext.parse(metadata_xml)

        return self.__get_summary(meta_doc)

    def get_files(self, package):
        files = Files.Files()
        files_xml = os.path.join(
            self.package_path(package),
            ctx.const.files_xml)
        files.read(files_xml)
        return files

    def get_config_files(self, package):
        files = self.get_files(package)
        return [x for x in files.list if x.type == 'config']

    def search_package(self, terms, lang=None, fields=None, cs=False):
        """
        fields (dict) : looks for terms in the fields which are marked as True
        If the fields is equal to None this method will search in all fields

        example :
        if fields is equal to : {'name': True, 'summary': True, 'desc': False}
        This method will return only package that contents terms in the package
        name or summary
        """
        resum = '<Summary xml:lang=.({0}|en).>.*?{1}.*?</Summary>'
        redesc = '<Description xml:lang=.({0}|en).>.*?{1}.*?</Description>'
        if not fields:
            fields = {'name': True, 'summary': True, 'desc': True}
        if not lang:
            lang = autoxml.LocalText.get_lang()
        found = []
        for name in self.list_installed():
            xml = open(
                os.path.join(
                    self.package_path(name),
                    ctx.const.metadata_xml)).read()
            if terms == [term for term in terms if (fields['name'] and
                                                    re.compile(term, re.I).search(name)) or
                                                   (fields['summary'] and
                                                    re.compile(resum.format(lang, term), 0 if cs else re.I).search(
                                                        xml)) or
                                                   (fields['desc'] and
                                                    re.compile(redesc.format(lang, term), 0 if cs else re.I).search(
                                                        xml))]:
                found.append(name)
        return found

    def get_isa_packages(self, isa):
        risa = '<IsA>{}</IsA>'.format(isa)
        packages = []
        for name in self.list_installed():
            xml = open(
                os.path.join(
                    self.package_path(name),
                    ctx.const.metadata_xml)).read()
            if re.compile(risa).search(xml):
                packages.append(name)
        return packages

    def get_info(self, package):
        files_xml = os.path.join(
            self.package_path(package),
            ctx.const.files_xml)
        ctime = inary.util.creation_time(files_xml)
        pkg = self.get_package(package)
        state = "i"
        if pkg.name in self.list_pending():
            state = "ip"

        info = InstallInfo(state,
                           pkg.version,
                           pkg.release,
                           pkg.distribution,
                           ctime)
        return info

    @staticmethod
    def __make_dependency(depStr):

        node = xmlext.parseString(depStr)

        dependency = inary.analyzer.dependency.Dependency()
        dependency.package = xmlext.getNodeText(node)

        if xmlext.getAttributeList(node):
            if xmlext.getNodeAttribute(node, "version"):
                dependency.__dict__[
                    "version"] = xmlext.getNodeAttribute(node, "version")
            elif xmlext.getNodeAttribute(node, "release"):
                dependency.__dict__[
                    "release"] = xmlext.getNodeAttribute(node, "release")
            else:
                pass  # FIXME: ugly
        return dependency

    def __create_dependency(self, depStr):
        if "<AnyDependency>" in depStr:
            anydependency = inary.data.specfile.AnyDependency()
            for dep in re.compile(
                    '(<Dependency .*?>.*?</Dependency>)').findall(depStr):
                anydependency.dependencies.append(self.__make_dependency(dep))
            return anydependency
        else:
            return self.__make_dependency(depStr)

    def get_rev_deps(self, name):
        rev_deps = []

        package_revdeps = self.rev_deps_db.get(name)
        if package_revdeps:
            for pkg, dep in list(package_revdeps.items()):
                dependency = self.__create_dependency(dep)
                rev_deps.append((pkg, dependency))

        return rev_deps

    def get_rev_dep_names(self, name):
        rev_deps = []

        package_revdeps = self.rev_deps_db.get(name)
        if package_revdeps:
            for pkg in list(package_revdeps.items()):
                rev_deps.append(pkg)

        return rev_deps

    def get_orphaned(self):
        """
        get list of packages installed as extra dependency,
        but without reverse dependencies now.
        """
        orphaned_packages = []
        for x in self.installed_extra:
            if not self.get_rev_deps(x):

                if x.endswith(
                        ctx.const.doc_package_end) and ctx.config.values.general.allow_docs:
                    if inary.util.remove_suffix(
                            ctx.const.doc_package_end, x) not in self.list_installed():
                        orphaned_packages.append(x)
                    else:
                        pass

                elif x.endswith(ctx.const.info_package_end) and ctx.config.values.general.allow_pages:
                    if inary.util.remove_suffix(
                            ctx.const.info_package_end, x) not in self.list_installed():
                        orphaned_packages.append(x)
                    else:
                        pass

                elif x.endswith(ctx.const.debug_name_suffix) and ctx.config.values.general.allow_dbginfo:
                    if inary.util.remove_suffix(
                            ctx.const.debug_name_suffix, x) not in self.list_installed():
                        orphaned_packages.append(x)
                    else:
                        pass

                elif x.endswith(ctx.const.static_name_suffix) and ctx.config.values.general.allow_static:
                    if inary.util.remove_suffix(
                            ctx.const.static_name_suffix, x) not in self.list_installed():
                        orphaned_packages.append(x)
                    else:
                        pass

                else:
                    orphaned_packages.append(x)

        return orphaned_packages

    def get_no_rev_deps(self):
        """
        get installed packages list which haven't reverse dependencies.
        """
        return [x for x in self.installed_db if not self.get_rev_deps(x)]

    @staticmethod
    def pkg_dir(pkg, version, release):
        return inary.util.join_path(
            ctx.config.packages_dir(), pkg + '-' + version + '-' + release)

    def get_package(self, package):
        metadata = inary.data.metadata.MetaData()
        metadata_xml = os.path.join(
            self.package_path(package),
            ctx.const.metadata_xml)
        metadata.read(metadata_xml)
        return metadata.package

    def get_metadata(self, package):
        metadata = inary.data.metadata.MetaData()
        metadata_xml = os.path.join(
            self.package_path(package),
            ctx.const.metadata_xml)
        metadata.read(metadata_xml)
        return metadata

    def __mark_package(self, _type, package):
        packages = self.__get_marked_packages(_type)
        if package not in packages:
            packages.append(package)
            self.__write_marked_packages(_type, packages)

    def mark_pending(self, package):
        self.__mark_package(ctx.const.config_pending, package)

    def mark_installed(self, package):
        self.__mark_package(ctx.const.config_installed, package)

    def mark_needs_restart(self, package):
        self.__mark_package(ctx.const.needs_restart, package)

    def mark_needs_reboot(self, package):
        self.__mark_package(ctx.const.needs_reboot, package)

    def add_package(self, pkginfo):
        # Cleanup old revdep info
        for revdep_info in list(self.rev_deps_db.values()):
            if pkginfo.name in revdep_info:
                del revdep_info[pkginfo.name]

        self.installed_db[pkginfo.name] = "{0.version}-{0.release}".format(
            pkginfo)
        self.__add_to_revdeps(pkginfo.name, self.rev_deps_db)

    def remove_package(self, package_name):
        if package_name in self.installed_db:
            del self.installed_db[package_name]

        # Cleanup revdep info
        for revdep_info in list(self.rev_deps_db.values()):
            if package_name in revdep_info:
                del revdep_info[package_name]

        self.clear_pending(package_name)

    def list_pending(self):
        return self.__get_marked_packages(ctx.const.config_pending)

    def __list_installed(self):
        return self.__get_marked_packages(ctx.const.config_installed)

    def list_needs_restart(self):
        return self.__get_marked_packages(ctx.const.needs_restart)

    def list_needs_reboot(self):
        return self.__get_marked_packages(ctx.const.needs_reboot)

    @staticmethod
    def __write_marked_packages(_type, packages):
        info_file = os.path.join(ctx.config.info_dir(), _type)
        config = open(info_file, "w")
        for pkg in set(packages):
            config.write("{}\n".format(pkg))
        config.close()

    def __clear_marked_packages(self, _type, package):
        if package == "*":
            self.__write_marked_packages(_type, [])
            return
        packages = self.__get_marked_packages(_type)
        if package in packages:
            packages.remove(package)
            self.__write_marked_packages(_type, packages)

    def clear_pending(self, package):
        self.__clear_marked_packages(ctx.const.config_pending, package)

    def clear_installed(self, package):
        self.__clear_marked_packages(ctx.const.config_installed, package)

    def clear_needs_restart(self, package):
        self.__clear_marked_packages(ctx.const.needs_restart, package)

    def clear_needs_reboot(self, package):
        self.__clear_marked_packages(ctx.const.needs_reboot, package)

    def package_path(self, package):

        if package in self.installed_db:
            return os.path.join(ctx.config.packages_dir(
            ), "{0}-{1}".format(package, self.installed_db[package]))

        raise Exception(_('Package \"{}\" is not installed.').format(package))
