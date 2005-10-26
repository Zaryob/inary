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
# Authors: Baris Metin <baris@uludag.org.tr>
#          Eray Ozkural <eray@uludag.org.tr>

"""
PISI Configuration module is used for gathering and providing
regular PISI configurations.
"""

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx
from pisi.configfile import ConfigurationFile
import pisi.util
from pisi.util import join_path as join

class Error(pisi.Error):
    pass

class Options(object):
    def __getattr__(self, name):
        if not self.__dict__.has_key(name):
            return None
        else:
            return self.__dict__[name]

class Config(object):
    """Config Singleton"""
    
    def __init__(self, options = Options()):
        self.options = options
        self.values = ConfigurationFile("/etc/pisi/pisi.conf")

    def get_option(self, opt):
        if self.options:
            if hasattr(self.options, opt):
                return getattr(self.options, opt)
        return None

    # directory accessor functions
    # here is how it goes
    # x_dir: system wide directory for storing info type x
    # pkg_x_dir: per package directory for storing info type x

    def dest_dir(self):
        dir = self.get_option('destdir')
        if dir:
            dir = str(dir)
        else:
            dir = self.values.general.destinationdirectory
        import os.path
        if not os.path.exists(dir):
            ctx.ui.warning( _('Destination directory %s does not exist. Creating it.') % dir)
            os.makedirs(dir)
        return dir

    def subdir(self, path):
        dir = join(self.dest_dir(), path)
        pisi.util.check_dir(dir)
        return dir

    def lib_dir(self):
        return self.subdir(self.values.dirs.lib_dir)

    def db_dir(self):
        return self.subdir(self.values.dirs.db_dir)

    def archives_dir(self):
        return self.subdir(self.values.dirs.archives_dir)

    def packages_dir(self):
        return self.subdir(self.values.dirs.packages_dir)

    def index_dir(self):
        return self.subdir(self.values.dirs.index_dir)

    def tmp_dir(self):
        return self.subdir(self.values.dirs.tmp_dir)

    # bu dizini neden kullanıyoruz? Yalnızca index.py içerisinde
    # kullanılıyor ama /var/tmp/pisi/install gibi bir dizine niye
    # ihtiyacımız var? (baris)
    def install_dir(self):
        return self.tmp_dir() + ctx.const.install_dir_suffix

#TODO: remove this
config = Config()
