# -*- coding: utf-8 -*-
# Context module.
# Authors: Baris Metin <baris@uludag.org.tr
#          Eray Ozkural <eray@uludag.org.tr>

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


class InstallContext(object):
    """Build Context Singleton"""

    class ctximpl(Config.configimpl):        # singleton implementation

        def __init(self):
            super(ctximpl, self).__init__()

        def setMetadataFile(self, metadatafile):
            self.metadatafile = metadatafile
            metadata = MetaData()
            metadata.read(metadatafile)
            metadata.verify()

            self.metadata = metadata

        def pkg_dir(self):
            packageDir = self.metadata.package.name + '-' \
                + self.metadata.package.version + '-' + self.metadata.package.release

            return self.destdir + config.lib_dir() \
                + '/' + packageDir

        def files_dir(self):
            return self.pkg_dir() + const.files_xml_dir_suffix

        def metadata_dir(self):
            return self.pkg_dir() + const.metadata_xml_dir_suffix
        
        def comar_dir(self):
            return self.pkg_dir() + const.comar_files_dir_suffix

    __instance = ctximpl()               # singleton implementation

    def __init__(self, mdfile):
        self.__instance.setMetadataFile(mdfile)

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)
