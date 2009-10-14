# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# PISI constants. 
# If you have a "magic" constant value this is where it should be
# defined.

# Author: Baris Metin <baris@uludag.org.tr

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi

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
        # prefix for package names
        self.__c.package_prefix = ".pisi"

        # directory suffixes for build
        self.__c.work_dir_suffix = "/work"
        self.__c.install_dir_suffix  = "/install"

        # file/directory names
        self.__c.actions_file = "actions.py"
        self.__c.files_dir = "files"
        self.__c.metadata_dir = "metadata"
        self.__c.comar_dir = "comar"
        self.__c.files_xml = "files.xml"
        self.__c.metadata_xml = "metadata.xml"
        self.__c.pisi_index = "pisi-index.xml"

        # functions in actions_file
        self.__c.setup_func = "setup"
        self.__c.build_func = "build"
        self.__c.install_func = "install"

        # file types
        self.__c.doc = "doc"
        self.__c.man = "man"
        self.__c.info = "info"
        self.__c.conf = "config"
        self.__c.header = "header"
        self.__c.library = "library"
        self.__c.executable = "executable"
        self.__c.data = "data"
        self.__c.localedata = "localedata"

    def __getattr__(self, attr):
        return getattr(self.__c, attr)

    def __setattr__(self, attr, value):
        setattr(self.__c, attr, value)

    def __delattr__(self, attr):
        delattr(self.__c, attr)
