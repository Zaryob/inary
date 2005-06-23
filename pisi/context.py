# -*- coding: utf-8 -*-
# PISI configuration (static and dynamic)

from specfile import SpecFile
from constants import const
from config import Config

class BuildContext(object):
    """Build Context Singleton"""

    class ctximpl(Config.configimpl):        # singleton implementation

        def __init(self):
            super(ctximpl, self).__init__()

        def setSpecFile(self, pspecfile):
            self.pspecfile = pspecfile
            spec = SpecFile()
            spec.read(pspecfile)
            spec.verify()    # check pspec integrity
            self.spec = spec

        # directory accessor functions
        
        # pkg_x_dir: per package directory for storing info type x

        def pkg_dir(self):
            packageDir = self.spec.source.name + '-' \
            + self.spec.source.version + '-' + self.spec.source.release

            return self.destdir + const.tmp_dir_suffix \
            + '/' + packageDir
   
        def pkg_work_dir(self):
            return self.pkg_dir() + const.work_dir_suffix

        def pkg_install_dir(self):
            return self.pkg_dir() + const.install_dir_suffix

    __instance = ctximpl()               # singleton implementation

    def __init__(self, pspecfile):
        self.__instance.setSpecFile(pspecfile)

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)
