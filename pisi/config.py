# PISI Configuration module is used for gathering and providing
# regular PISI configurations.

# Authors: Baris Metin <baris@uludag.org.tr
#          Eray Ozkural <eray@uludag.org.tr>

#TODO: Eventually PISI will have a configuration file (located in
#/etc/pisi/conf?) and this module will provide access to those
#configuration parameters.

from constants import const
from configfile import ConfigurationFile

class Config(object):
    """Config Singleton"""
    
    class configimpl:

        def __init__(self):
            self.conf = ConfigurationFile("/etc/pisi/pisi.conf")
            self.destdir = self.conf.general.destinationdirectory
            self.username = self.conf.svn.username
            self.password = self.conf.svn.password

        # directory accessor functions
        # here is how it goes
        # x_dir: system wide directory for storing info type x
        # pkg_x_dir: per package directory for storing info type x

        def lib_dir(self):
            return self.destdir + const.lib_dir_suffix

        def db_dir(self):
            return self.destdir + const.db_dir_suffix

        def archives_dir(self):
            return self.destdir + const.archives_dir_suffix
    
        def tmp_dir(self):
            return self.destdir + const.tmp_dir_suffix

        def install_dir(self):
            return self.tmp_dir() + const.install_dir_suffix

    __configinstance = configimpl()

    def __init__(self):
        pass

    def __getattr__(self, attr):
        return getattr(self.__configinstance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__configinstance, attr, value)


config = Config()
