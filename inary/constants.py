# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

"""INARY constants.
If you have a "magic" constant value this is where it should be
defined."""

import gettext

__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)

        return cls.instance


class _constant:
    """Constant members implementation"""

    class ConstError(TypeError):
        pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError(_("Can't rebind constant: \'{}\'").format(name))
        # Binding an attribute once to a const is available
        self.__dict__[name] = value

    def __delattr__(self, name):
        if name in self.__dict__:
            raise self.ConstError(_("Can't unbind constant: \'{}\'").format(name))
        # we don't have an attribute by this name
        raise NameError(name)


class Constants(metaclass=Singleton):
    """Inary Constants Singleton"""

    __c = _constant()

    def __init__(self):
        # suffix for package names
        self.__c.package_suffix = ".inary"

        # delta suffix for package names
        self.__c.delta_package_suffix = ".delta.inary"

        # suffix for lzma
        self.__c.lzma_suffix = ".lzma"
        # suffix for xz
        self.__c.xz_suffix = ".xz"

        self.__c.partial_suffix = ".part"
        self.__c.temporary_suffix = ".tmp"

        # suffix for auto generated debug packages
        self.__c.debug_name_suffix = "-dbginfo"
        self.__c.debug_file_suffix = ".debug"
        self.__c.debug_file_buildid = ".build-id"

        # suffix for auto generated ar packages
        self.__c.static_name_suffix = "-static"  # an admissible use of constant
        self.__c.ar_file_suffix = ".a"

        # directory suffixes for build
        self.__c.work_dir_suffix = "/work"  # these, too, because we might wanna change 'em
        self.__c.install_dir_suffix = "/install"
        self.__c.debug_dir_suffix = "/debug"
        self.__c.debug_files_suffix = "/usr/lib/debug"
        self.__c.quilt_dir_suffix = "/patches"

        # file/directory names
        # note: these don't seem very well, constants are used
        # when it is easier/more meaningful to write the constant name, or
        # when the constant is bound to change later on.
        # in some places literals are just as good, for instance
        # when constant is the same as string. readability is important...
        self.__c.actions_file = "actions.py"
        self.__c.pspec_file = "pspec.xml"
        self.__c.files_dir = "files"
        self.__c.metadata_dir = "metadata"
        self.__c.translations_file = "translations.xml"
        self.__c.scom_dir = "scom"
        self.__c.files_xml = "files.xml"
        self.__c.metadata_xml = "metadata.xml"
        self.__c.install_tar = "install.tar"
        self.__c.mirrors_conf = "/etc/inary/mirrors.conf"
        self.__c.sandbox_conf = "/etc/inary/sandbox.conf"
        self.__c.blacklist = "/etc/inary/blacklist"
        self.__c.config_pending = "configpending"
        self.__c.needs_restart = "needsrestart"
        self.__c.needs_reboot = "needsreboot"
        self.__c.files_db = "files"
        self.__c.repos = "repos"
        self.__c.devel_package_end = "-devel"
        self.__c.info_package_end = "-pages"
        self.__c.doc_package_end = "-docs?$"
        self.__c.assign_to_system_devel = ["system.base", "system.devel"]
        self.__c.system_devel_component = "system.devel"
        self.__c.devels_component = "programming.devel"
        self.__c.docs_component = "programming.docs"
        self.__c.installed_extra = "installedextra"

        # file/directory permissions
        self.__c.umask = 0o022

        # functions in actions_file
        self.__c.setup_func = "setup"
        self.__c.build_func = "build"
        self.__c.check_func = "check"
        self.__c.install_func = "install"

        # file types
        # FIXME: these seem redundant
        self.__c.doc = "doc"
        self.__c.man = "man"
        self.__c.info = "info"
        self.__c.conf = "config"
        self.__c.header = "header"
        self.__c.library = "library"
        self.__c.executable = "executable"
        self.__c.data = "data"
        self.__c.localedata = "localedata"
        self.__c.colors = {
                           'black': "30",
                           'red': "31",
                           'green': "32",
                           'yellow': "33",
                           'blue': "34",
                           'purple': "35",
                           'cyan': "36",
                           'white': "37",
                            }
        self.__c.backgrounds = {
                           'black': "40",
                           'red': "41",
                           'green': "42",
                           'yellow': "43",
                           'blue': "44",
                           'purple': "45",
                           'cyan': "46",
                           'white': "47",
                            }
        self.__c.attrs = {
                           'normal': "0",
                           'bright': "1",
                           'faint': "2",
                           'italic': "3",
                           'underline': "4",
                           'blinking': "5",
                           'rapidblinking': "6",
                           'reverse': "7",
                           'invisible': "8",
                           'strikethrough': "9"
                           }

    def __getattr__(self, attr):
        return getattr(self.__c, attr)

    def __setattr__(self, attr, value):
        setattr(self.__c, attr, value)

    def __delattr__(self, attr):
        delattr(self.__c, attr)
