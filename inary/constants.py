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

"""INARY constants.
If you have a "magic" constant value this is where it should be
defined."""

# Gettext Library
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
            raise self.ConstError(
                _("Can't rebind constant: \'{}\'").format(name))
        # Binding an attribute once to a const is available
        self.__dict__[name] = value

    def __delattr__(self, name):
        if name in self.__dict__:
            raise self.ConstError(
                _("Can't unbind constant: \'{}\'").format(name))
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
        # suffix for gz
        self.__c.gz_suffix = ".gz"

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
        # these, too, because we might wanna change 'em
        self.__c.work_dir_suffix = "/work"
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
        self.__c.files_xml = "files.xml"
        self.__c.metadata_xml = "metadata.xml"
        self.__c.postops = ["postoperations.py", "postoperations.sh"]
        self.__c.install_tar = "install.tar"
        self.__c.mirrors_conf = "/etc/inary/mirrors.conf"
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
        self.__c.colors = {'black': "\033[30m",
                           'red': "\033[31m",
                           'green': "\033[32m",
                           'yellow': "\033[33m",
                           'blue': "\033[34m",
                           'purple': "\033[35m",
                           'cyan': "\033[36m",
                           'white': "\033[37m",
                           'brightblack': "\033[01;30m",
                           'brightred': "\033[01;31m",
                           'brightgreen': "\033[01;32m",
                           'brightyellow': "\033[01;33m",
                           'brightblue': "\033[01;34m",
                           'brightpurple': "\033[01;35m",
                           'brightcyan': "\033[01;36m",
                           'brightwhite': "\033[01;37m",
                           'faintblack': "\033[02;30m",
                           'faintred': "\033[02;31m",
                           'faintgreen': "\033[02;32m",
                           'faintyellow': "\033[02;33m",
                           'faintblue': "\033[02;34m",
                           'faintpurple': "\033[02;35m",
                           'faintcyan': "\033[02;36m",
                           'faintwhite': "\033[02;37m",
                           'italicblack': "\033[03;30m",
                           'italicred': "\033[03;31m",
                           'italicgreen': "\033[03;32m",
                           'italicyellow': "\033[03;33m",
                           'italicblue': "\033[03;34m",
                           'italicpurple': "\033[03;35m",
                           'italiccyan': "\033[03;36m",
                           'italicwhite': "\033[03;37m",
                           'underlineblack': "\033[04;30m",
                           'underlinered': "\033[04;31m",
                           'underlinegreen': "\033[04;32m",
                           'underlineyellow': "\033[04;33m",
                           'underlineblue': "\033[04;34m",
                           'underlinemagenta': "\033[04;35m",
                           'underlinecyan': "\033[04;36m",
                           'underlinewhite': "\033[04;37m",
                           'blinkingblack': "\033[05;30m",
                           'blinkingred': "\033[05;31m",
                           'blinkinggreen': "\033[05;32m",
                           'blinkingyellow': "\033[05;33m",
                           'blinkingblue': "\033[05;34m",
                           'blinkingmagenta': "\033[05;35m",
                           'blinkingcyan': "\033[05;36m",
                           'blinkingwhite': "\033[05;37m",
                           'backgroundblack': "\033[07;30m",
                           'backgroundred': "\033[07;31m",
                           'backgroundgreen': "\033[07;32m",
                           'backgroundyellow': "\033[07;33m",
                           'backgroundblue': "\033[07;34m",
                           'backgroundmagenta': "\033[07;35m",
                           'backgroundcyan': "\033[07;36m",
                           'backgroundwhite': "\033[07;37m",
                           'strikethroughblack': "\033[09;30m",
                           'strikethroughred': "\033[09;31m",
                           'strikethroughgreen': "\033[09;32m",
                           'strikethroughyellow': "\033[09;33m",
                           'strikethroughblue': "\033[09;34m",
                           'strikethroughmagenta': "\033[09;35m",
                           'strikethroughcyan': "\033[09;36m",
                           'strikethroughwhite': "\033[09;37m",
                           'default': "\033[0m"}

    def __getattr__(self, attr):
        return getattr(self.__c, attr)

    def __setattr__(self, attr, value):
        setattr(self.__c, attr, value)

    def __delattr__(self, attr):
        delattr(self.__c, attr)
