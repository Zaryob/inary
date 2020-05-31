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

# Standart Python Libraries
import os

# Inary Modules
import inary.db
import inary.ui as ui
import inary.util as util
import inary.context as ctx
import inary.analyzer.conflict

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


def reorder_base_packages(order):
    componentdb = inary.db.componentdb.ComponentDB()

    """system.base packages must be first in order"""
    systembase = componentdb.get_union_component('system.base').packages

    systembase_order = []
    nonbase_order = []
    for pkg in order:
        if pkg in systembase:
            systembase_order.append(pkg)
        else:
            nonbase_order.append(pkg)

    return systembase_order + nonbase_order


def check_conflicts(order, packagedb):
    """check if upgrading to the latest versions will cause havoc
    done in a simple minded way without regard for dependencies of
    conflicts, etc."""

    (C, D, pkg_conflicts) = inary.analyzer.conflict.calculate_conflicts(order, packagedb)

    if D:
        raise Exception(
            _("Selected packages \"[{}]\" are in conflict with each other.").format(
                util.strlist(
                    list(D))))

    if pkg_conflicts:
        conflicts = ""
        for pkg in list(pkg_conflicts.keys()):
            conflicts += _(" - [\"{0}\" conflicts with: \"{1}\"]\n").format(
                pkg, util.strlist(pkg_conflicts[pkg]))

        ctx.ui.info(
            _("The following packages have conflicts:\n{}").format(conflicts))

        if not ctx.ui.confirm(_('Remove the following conflicting packages?')):
            raise Exception(
                _("Conflicting packages should be removed to continue."))

    return list(C)


def expand_src_components(A):
    componentdb = inary.db.componentdb.ComponentDB()
    Ap = set()
    for x in A:
        if componentdb.has_component(x):
            Ap = Ap.union(componentdb.get_union_component(x).sources)
        else:
            Ap.add(x)
    return Ap


def calculate_free_space_needed(order):
    total_needed = 0
    installdb = inary.db.installdb.InstallDB()
    packagedb = inary.db.packagedb.PackageDB()

    for pkg in [packagedb.get_package(name) for name in order]:
        delta = None
        if installdb.has_package(pkg.name):
            release = installdb.get_release(pkg.name)
            (distro, distro_release) = installdb.get_distro_release(pkg.name)

            # inary distro upgrade should not use delta support
            if distro == pkg.distribution and distro_release == pkg.distributionRelease:
                delta = pkg.get_delta(release)

            ignore_delta = ctx.config.values.general.ignore_delta

            installed_release_size = installdb.get_package(
                pkg.name).installedSize

            if delta and not ignore_delta:
                pkg_size = delta.installedSize
            else:
                pkg_size = pkg.installedSize - installed_release_size

            total_needed += pkg_size

        else:
            total_needed += int(packagedb.get_package(pkg.name).installedSize)

    needed, symbol = util.human_readable_size(total_needed)

    if total_needed < 0:
        ctx.ui.info(_("After this operation, {:.2f} {} space will be freed.").format(
            abs(int(needed)), symbol), color='cyan')
    else:
        ctx.ui.info(_("After this operation, {:.2f} {} space will be used.").format(
            abs(int(needed)), symbol), color='cyan')

    return total_needed


def calculate_download_sizes(order):
    total_size = cached_size = 0
    installdb = inary.db.installdb.InstallDB()
    packagedb = inary.db.packagedb.PackageDB()

    try:
        cached_packages_dir = ctx.config.cached_packages_dir()
    except OSError:
        # happens when cached_packages_dir tried to be created by an
        # unpriviledged user
        cached_packages_dir = None

    for pkg in [packagedb.get_package(name) for name in order]:
        delta = None
        if installdb.has_package(pkg.name):
            release = installdb.get_release(pkg.name)
            (distro, distro_release) = installdb.get_distro_release(pkg.name)

            # inary distro upgrade should not use delta support
            if distro == pkg.distribution and distro_release == pkg.distributionRelease:
                delta = pkg.get_delta(release)

        ignore_delta = ctx.config.values.general.ignore_delta

        if delta and not ignore_delta:
            fn = os.path.basename(delta.packageURI)
            pkg_hash = delta.packageHash
            pkg_size = delta.packageSize
        else:
            fn = os.path.basename(pkg.packageURI)
            pkg_hash = pkg.packageHash
            pkg_size = pkg.packageSize

        if cached_packages_dir:
            path = util.join_path(cached_packages_dir, fn)
            # check the file and sha1sum to be sure it _is_ the cached package
            if os.path.exists(path) and util.sha1_file(path) == pkg_hash:
                cached_size += pkg_size
            elif os.path.exists("{}.part".format(path)):
                cached_size += os.stat("{}.part".format(path)).st_size

        total_size += pkg_size

    ctx.ui.notify(
        ui.cached,
        logging=False,
        total=total_size,
        cached=cached_size)
    return total_size, cached_size


def get_package_requirements(packages):
    """
    Returns a dict with two keys - systemRestart, serviceRestart - with package lists as their values
    @param packages: list of package names -> list_of_strings

    >>> lu = inary.api.list_upgrades()

    >>> requirements = inary.api.get_package_requirements(lu)

    >>> print requirements
    >>> { "systemRestart":["kernel", "module-alsa-driver"], "serviceRestart":["mysql-server", "memcached", "postfix"] }

    """

    actions = ("systemRestart", "serviceRestart")
    requirements = dict((action, []) for action in actions)

    installdb = inary.db.installdb.InstallDB()
    packagedb = inary.db.packagedb.PackageDB()

    for i_pkg in packages:
        try:
            pkg = packagedb.get_package(i_pkg)
        except Exception:  # FIXME: Should catch RepoItemNotFound exception
            pass

        release = installdb.get_release(i_pkg)
        pkg_actions = pkg.get_update_actions(release)

        for action_name in pkg_actions:
            if action_name in actions:
                requirements[action_name].append(pkg.name)

    return requirements


def check_config_changes(order, opt=None):
    if not opt:
        import inary.data.history as History
        history = History.History()
        opt = "%03d" % (int(history._get_latest()) - 1)

    config_changes = dict()
    installdb = inary.db.installdb.InstallDB()
    if not os.path.exists(os.path.join(ctx.config.history_dir(), opt)):
        return []

    for package in order:
        all_files = installdb.get_files(package)
        config_files = [x for x in all_files.list if x.type == 'config']
        config_paths = ["/" + str(x.path) for x in config_files]

        newconfig = []

        for path in config_paths:
            if os.path.exists(os.path.join(
                    ctx.config.history_dir(), opt, path)) and os.path.exists(path):
                newconfig.append(path)
        if newconfig:
            config_changes[package] = newconfig

    return config_changes, opt


def apply_changed_config(old_file, new_file, keep=True):
    if keep:
        ctx.ui.info(
            _("Keeping old config file {0} as {0}.old-byinary").format(old_file),
            verbose=True)
        util.copy_file(old_file, old_file + ".old-byinary")
    util.copy_file(new_file, old_file)
    util.delete_file(new_file)


def show_changed_configs(package_dict, opt):
    for package in package_dict:
        if package_dict[package]:
            if ctx.ui.confirm(util.colorize(
                    _("[?] Would you like to see changes in config files of \"{0}\" package").format(package), color='brightyellow')):
                for file in package_dict[package]:
                    new_file = util.join_path(
                        ctx.config.history_dir(), opt, package, ctx.config.dest_dir(), file)

                    if os.path.exists(new_file):
                        ctx.ui.info(
                            _("[*] Changes in config file: {}").format(file),
                            color='yellow')
                        os.system(
                            "diff -u {0} {1} | less".format(new_file, file))
                        prompt = ctx.ui.choose(_("[?] Select the process which will be happened:"),
                                               [_("1. Store new config file, not apply [*]"),
                                                _("2. Apply new config file (keep old config)"),
                                                _("3. Apply new config file (don't keep old config)"),
                                                _("4. Delete new config file")])

                        if prompt == _(
                                "1. Store new config file, not apply [*]"):
                            pass
                        elif prompt == _("2. Apply new config file (keep old config)"):
                            apply_changed_config(
                                util.join_path(
                                    ctx.config.dest_dir(),
                                    file),
                                new_file,
                                keep=True)
                        elif prompt == _("3. Apply new config file (don't keep old config)"):
                            apply_changed_config(
                                util.join_path(
                                    ctx.config.dest_dir(),
                                    file),
                                new_file,
                                keep=False)

                        else:
                            ctx.ui.info(
                                _("Deleting new config file {0}").format(file), verbose=True)
                            util.delete_file(new_file)
