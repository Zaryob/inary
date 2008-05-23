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

"""PiSi constants.
If you have a "magic" constant value this is where it should be
defined."""

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

class _constant:
    "Constant members implementation"
    class ConstError(TypeError):
        pass

    def __setattr__(self, name, value):
        if self.__dict__.has_key(name):
            raise self.ConstError, _("Can't rebind constant: %s") % name
        # Binding an attribute once to a const is available
        self.__dict__[name] = value

    def __delattr__(self, name):
        if self.__dict__.has_key(name):
            raise self.ConstError, _("Can't unbind constant: %s") % name
        # we don't have an attribute by this name
        raise NameError, name

class Constants:
    "Pisi Constants Singleton"

    __c = _constant()

    def __init__(self):
        # suffix for package names
        self.__c.package_suffix = ".pisi"

        # delta suffix for package names
        self.__c.delta_package_suffix = ".delta.pisi"

        # suffix for lzma
        self.__c.lzma_suffix = ".lzma"

        # suffix for auto generated debug packages
        self.__c.debug_name_suffix = "-debug"
        self.__c.debug_file_suffix = ".debug"

        # suffix for auto generated ar packages
        self.__c.static_name_suffix = "-static"  # an admissible use of constant
        self.__c.ar_file_suffix = ".a"

        # directory suffixes for build
        self.__c.work_dir_suffix = "/work"       # these, too, because we might wanna change 'em
        self.__c.install_dir_suffix  = "/install"
        self.__c.debug_dir_suffix  = "/debug"
        self.__c.debug_files_suffix  = "/usr/lib/debug"
        self.__c.quilt_dir_suffix  = "/patches"

        # file/directory names
        #note: these don't seem very well, constants are used
        #when it is easier/more meaningful to write the constant name, or
        #when the constant is bound to change later on.
        #in some places literals are just as good, for instance
        #when constant is the same as string. readability is important...
        self.__c.actions_file = "actions.py"
        self.__c.pspec_file = "pspec.xml"
        self.__c.files_dir = "files"
        self.__c.metadata_dir = "metadata"
        self.__c.translations_file = "translations.xml"
        self.__c.comar_dir = "comar"
        self.__c.files_xml = "files.xml"
        self.__c.metadata_xml = "metadata.xml"
        self.__c.install_tar = "install.tar"
        self.__c.install_tar_lzma = "install.tar.lzma"
        self.__c.mirrors_conf = "/etc/pisi/mirrors.conf"
        self.__c.sandbox_conf = "/etc/pisi/sandbox.conf"
        self.__c.blacklist = "/etc/pisi/blacklist"
        self.__c.config_pending = "configpending"
        self.__c.files_db = "files.db"
        self.__c.repos = "repos"
        
        #file/directory permissions
        self.__c.umask = 0022

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
        self.__c.colors = {'black'              : "\033[30m",
                           'red'                : "\033[31m",
                           'green'              : "\033[32m",
                           'yellow'             : "\033[33m",
                           'blue'               : "\033[34m",
                           'purple'             : "\033[35m",
                           'cyan'               : "\033[36m",
                           'white'              : "\033[37m",
                           'brightblack'        : "\033[01;30m",
                           'brightred'          : "\033[01;31m",
                           'brightgreen'        : "\033[01;32m",
                           'brightyellow'       : "\033[01;33m",
                           'brightblue'         : "\033[01;34m",
                           'brightmagenta'      : "\033[01;35m",
                           'brightcyan'         : "\033[01;36m",
                           'brightwhite'        : "\033[01;37m",
                           'underlineblack'     : "\033[04;30m",
                           'underlinered'       : "\033[04;31m",
                           'underlinegreen'     : "\033[04;32m",
                           'underlineyellow'    : "\033[04;33m",
                           'underlineblue'      : "\033[04;34m",
                           'underlinemagenta'   : "\033[04;35m",
                           'underlinecyan'      : "\033[04;36m",
                           'underlinewhite'     : "\033[04;37m",
                           'blinkingblack'      : "\033[05;30m",
                           'blinkingred'        : "\033[05;31m",
                           'blinkinggreen'      : "\033[05;32m",
                           'blinkingyellow'     : "\033[05;33m",
                           'blinkingblue'       : "\033[05;34m",
                           'blinkingmagenta'    : "\033[05;35m",
                           'blinkingcyan'       : "\033[05;36m",
                           'blinkingwhite'      : "\033[05;37m",
                           'backgroundblack'    : "\033[07;30m",
                           'backgroundred'      : "\033[07;31m",
                           'backgroundgreen'    : "\033[07;32m",
                           'backgroundyellow'   : "\033[07;33m",
                           'backgroundblue'     : "\033[07;34m",
                           'backgroundmagenta'  : "\033[07;35m",
                           'backgroundcyan'     : "\033[07;36m",
                           'backgroundwhite'    : "\033[07;37m",
                           'default'            : "\033[0m"  }

    def __getattr__(self, attr):
        return getattr(self.__c, attr)

    def __setattr__(self, attr, value):
        setattr(self.__c, attr, value)

    def __delattr__(self, attr):
        delattr(self.__c, attr)
