# -*- coding: utf-8 -*-
#
# Copyright (C) 2006, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

class _constant:
    "Constant members implementation"
    class ConstError(TypeError):
        pass

    def __setattr__(self, name, value):
        if self.__dict__.has_key(name):
            raise self.ConstError, "Can't rebind constant: %s" % name
        # Binding an attribute once to a const is available
        self.__dict__[name] = value

    def __delattr__(self, name):
        if self.__dict__.has_key(name):
            raise self.ConstError, "Can't unbind constant: %s" % name
        # we don't have an attribute by this name
        raise NameError, name

class Constants:

    __c = _constant()

    def __getattr__(self, attr):
        return getattr(self.__c, attr)

    def __setattr__(self, attr, value):
        setattr(self.__c, attr, value)

    def __delattr__(self, attr):
        delattr(self.__c, attr)

consts = Constants()

consts.scenarios_path = "scenarios/"
consts.pisi_db = "db/"
consts.repo_name = "scenario-db"
consts.repo_path = "repo/"
consts.repo_url = consts.repo_path + "pisi-index.xml"

consts.glob_pisis = "*.pisi"
consts.pisi_suffix = ".pisi"

consts.pspec_path = "/tmp/pspec.xml"
consts.actionspy_path = "/tmp/actions.py"

consts.packager_name = "Faik Uygur"
consts.packager_email = "faik@pardus.org.tr"

consts.homepage = "http://cekirdek.uludag.org.tr/~faik/pisi"
consts.summary = "%s is a good application"
consts.description = "%s is a free software that can do anything it wants"
consts.license = ["GPL-2"]

consts.skel_sha1sum = "cc64dfa6e068fe1f6fb68a635878b1ea21acfac7"
consts.skel_type = "targz"
consts.skel_uri = "http://cekirdek.uludag.org.tr/~faik/pisi/skeleton.tar.gz"
consts.skel_bindir = "/usr/bin"
consts.skel_dirtype = "executable"
