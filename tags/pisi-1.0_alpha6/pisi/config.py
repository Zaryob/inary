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
from pisi.util import join_path as join

class Config(object):
    """Config Singleton"""
    
    def __init__(self, options = None):
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
            raise Exception, _('Destination directory %s does not exist') % dir
        return dir

    def lib_dir(self):
        return join(self.dest_dir(), self.values.dirs.lib_dir)

    def db_dir(self):
        return join(self.dest_dir(), self.values.dirs.db_dir)

    def archives_dir(self):
        return join(self.dest_dir(), self.values.dirs.archives_dir)

    def packages_dir(self):
        return join(self.dest_dir(), self.values.dirs.packages_dir)

    def index_dir(self):
        return join(self.dest_dir(), self.values.dirs.index_dir)

    def tmp_dir(self):
        return join(self.dest_dir(), self.values.dirs.tmp_dir)

    # bu dizini neden kullanıyoruz? Yalnızca index.py içerisinde
    # kullanılıyor ama /var/tmp/pisi/install gibi bir dizine niye
    # ihtiyacımız var? (baris)
    def install_dir(self):
        return self.tmp_dir() + ctx.const.install_dir_suffix

#TODO: remove this
config = Config()
