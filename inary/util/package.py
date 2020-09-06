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

"""misc. utility functions, including process and file utils"""

# Inary Modules
from inary.util.strings import *
import inary
import inary.errors
import inary.context as ctx

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


########################################
# Package/Repository Related Functions #
########################################


def package_filename(name, version, release, distro_id=None, arch=None):
    """Return a filename for a package with the given information. """

    if distro_id is None:
        distro_id = ctx.config.values.general.distribution_id

    if arch is None:
        arch = ctx.config.values.general.architecture

    fn = "-".join((name, version, release, distro_id, arch))
    fn += ctx.const.package_suffix

    return fn


def parse_package_name_legacy(package_name):
    """Separate package name and version string for package formats <= 1.1.

    example: tasma-1.0.3-5-2 -> (tasma, 1.0.3-5-2)
    """
    # We should handle package names like 855resolution
    name = []
    for part in package_name.split("-"):
        if name != [] and part[0] in digits:
            break
        else:
            name.append(part)
    name = "-".join(name)
    version = package_name[len(name) + 1:]

    return name, version


def parse_package_name(package_name):
    """Separate package name and version string.

    example: tasma-1.0.3-5-p11-x86_64 -> (tasma, 1.0.3-5)
    """

    # Strip extension if exists
    if package_name.endswith(ctx.const.package_suffix):
        package_name = remove_suffix(ctx.const.package_suffix, package_name)

    try:
        name, version, release, distro_id, arch = package_name.rsplit("-", 4)

        # Arch field cannot start with a digit. If a digit is found,
        # the package might have an old format. Raise here to call
        # the legacy function.
        if not arch or arch[0] in digits:
            raise ValueError

    except ValueError:
        try:
            return parse_package_name_legacy(package_name)
        except BaseException:
            raise Error(_("Invalid package name: \"{}\"").format(package_name))

    return name, "{0}-{1}".format(version, release)


def parse_package_name_get_name(package_name):
    """Separate package name and version string.

    example: tasma-1.0.3-5-p11-x86_64 -> (tasma, 1.0.3-5)
    """

    # Strip extension if exists
    if package_name.endswith(ctx.const.package_suffix):
        package_name = remove_suffix(ctx.const.package_suffix, package_name)
    name = package_name.rsplit("-", 4)[0]
    return name


def parse_package_dir_path(package_name):
    name = parse_package_name(package_name)[0]
    if name.split("-").pop() in ["devel", "32bit", "doc", "docs", "pages", "static", "dbginfo", "32bit-dbginfo",
                                 "userspace"]:
        name = name[:-1 - len(name.split("-").pop())]
    return "{0}/{1}".format(name[0:4].lower() if name.startswith("lib") and len(name) > 3 else name.lower()[0],
                            name.lower())


def parse_delta_package_name_legacy(package_name):
    """Separate delta package name and release infos for package formats <= 1.1.

    example: tasma-5-7.delta.inary -> (tasma, 5, 7)
    """
    name, build = parse_package_name(package_name)
    build = build[:-len(ctx.const.delta_package_suffix)]
    buildFrom, buildTo = build.split("-")

    return name, buildFrom, buildTo


def parse_delta_package_name(package_name):
    """Separate delta package name and release infos

    example: tasma-5-7-p11-x86_64.delta.inary -> (tasma, 5, 7)
    """

    # Strip extension if exists
    if package_name.endswith(ctx.const.delta_package_suffix):
        package_name = remove_suffix(ctx.const.delta_package_suffix,
                                     package_name)

    try:
        name, source_release, target_release, distro_id, arch = \
            package_name.rsplit("-", 4)

        # Arch field cannot start with a digit. If a digit is found,
        # the package might have an old format. Raise here to call
        # the legacy function.
        if not arch or arch[0] in digits:
            raise ValueError

    except ValueError:
        try:
            return parse_delta_package_name_legacy(package_name)
        except BaseException:
            raise Error(
                _("Invalid delta package name: \"{}\"").format(package_name))

    return name, source_release, target_release


def split_package_filename(filename):
    """Split fields in package filename.

    example: tasma-1.0.3-5-p11-x86_64.inary -> (tasma, 1.0.3, 5, p11, x86_64)
    """

    # Strip extension if exists
    if filename.endswith(ctx.const.package_suffix):
        filename = remove_suffix(ctx.const.package_suffix, filename)

    try:
        name, version, release, distro_id, arch = filename.rsplit("-", 4)

        # Arch field cannot start with a digit. If a digit is found,
        # the package might have an old format.
        if not arch or arch[0] in digits:
            raise ValueError

    except ValueError:
        name, version = parse_package_name_legacy(filename)
        version, release = split_version(version)[:2]
        distro_id = arch = None

    return name, version, release, distro_id, arch


def split_delta_package_filename(filename):
    """Split fields in delta package filename.

    example: tasma-5-7-p11-x86_64.delta.inary -> (tasma, 5, 7, p11, x86-64)
    """

    # Strip extension if exists
    if filename.endswith(ctx.const.delta_package_suffix):
        filename = remove_suffix(ctx.const.delta_package_suffix, filename)

    try:
        name, source_release, target_release, distro_id, arch = \
            filename.rsplit("-", 4)

        # Arch field cannot start with a digit. If a digit is found,
        # the package might have an old format.
        if not arch or arch[0] in digits:
            raise ValueError

    except ValueError:
        # Old formats not supported
        name = parse_delta_package_name_legacy(filename)[0]
        source_release = target_release = None

    return name, source_release, target_release, distro_id, arch


def split_version(package_version):
    """Split version, release and build parts of a package version

    example: 1.0.3-5-2 -> (1.0.3, 5, 2)
    """
    version, sep, release_and_build = package_version.partition("-")
    release, sep, build = release_and_build.partition("-")
    return version, release, build


def filter_latest_packages(package_paths):
    """ For a given inary package paths list where there may also be multiple versions
        of the same package, filters only the latest versioned ones """

    import inary.version

    latest = {}
    for path in package_paths:

        name, version = parse_package_name(
            os.path.basename(path[:-len(ctx.const.package_suffix)]))

        if name in latest:
            l_version, l_release, l_build = split_version(latest[name][1])
            r_version, r_release, r_build = split_version(version)

            try:
                l_release = int(l_release)
                r_release = int(r_release)

                l_build = int(l_build) if l_build else None
                r_build = int(r_build) if r_build else None

            except ValueError:
                continue

            if l_build and r_build:
                if l_build > r_build:
                    continue

            elif l_release > r_release:
                continue

            elif l_release == r_release:
                l_version = inary.version.make_version(l_version)
                r_version = inary.version.make_version(r_version)

                if l_version > r_version:
                    continue

        if version:
            latest[name] = (path, version)

    return [x[0] for x in list(latest.values())]
