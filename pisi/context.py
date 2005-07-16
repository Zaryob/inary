# -*- coding: utf-8 -*-
# Context module.
# Authors: Baris Metin <baris@uludag.org.tr
#          Eray Ozkural <eray@uludag.org.tr>

from constants import const
from config import Config
from specfile import SpecFile
from package import Package
from metadata import MetaData
from files import Files

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

        def setPackage(self, packagefile):
            self.packagefile = packagefile
            self.package = Package(packagefile, 'r')

            tmpdir = self.tmp_dir()
            # extract control files
            self.package.extract_PISI_files(tmpdir)

            # read files.xml and metadata.xml
            mdxml = tmpdir + '/' + const.metadata_xml
            self.setMetadataXML(mdxml)
            filesxml = tmpdir + '/' + const.files_xml
            self.setFilesXML(filesxml)

        def setMetadataXML(self, metadataxml):
            self.metadataxml = metadataxml
            metadata = MetaData()
            metadata.read(metadataxml)
            if not metadata.verify():
                raise InstallError("MetaData format wrong")

            self.metadata = metadata

        def setFilesXML(self, filesxml):
            self.filesxml = filesxml
            files = Files()
            files.read(filesxml)

            self.files = files

        def pkg_dir(self):
            packageDir = self.metadata.package.name + '-' \
                + self.metadata.package.version + '-' \
                + self.metadata.package.release

            return self.lib_dir() + '/' + packageDir

        def comar_dir(self):
            return self.pkg_dir() + const.comar_dir_suffix

    __instance = ctximpl()               # singleton implementation

    def __init__(self, packagefile):
        self.__instance.setPackage(packagefile)

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)
