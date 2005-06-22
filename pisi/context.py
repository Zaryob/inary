# -*- coding: utf-8 -*-
# PISI configuration (static and dynamic)

from specfile import SpecFile
import oo

class Constants:
    "Pisi constants"

    c = oo.const()

    def __init__(self):
        # Metadata 
        #TODO: These two will be defined in a configuration file.
        self.c.distribution = "Pardus"
        self.c.distributionRelease = "0.1"

        self.c.lib_dir_suffix = "/var/lib/pisi"
        self.c.db_dir_suffix = "/var/db/pisi"
        self.c.archives_dir_suffix = "/var/cache/pisi/archives"
        self.c.tmp_dir_suffix =  "/var/tmp/pisi"

        # directory suffixes for build
        self.c.work_dir_suffix = "/work"
        self.c.install_dir_suffix  = "/install"

        # file/directory names
        self.c.actions_file = "actions.py"
        self.c.files_dir = "files"

        # functions in actions_file
        self.c.setup_func = "setup"
        self.c.build_func = "build"
        self.c.install_func = "install"

    def __getattr__(self, attr):
        return getattr(self.c, attr)

    def __setattr__(self, attr, value):
        return setattr(self.c, attr, value)

    def __delattr__(self, attr):
        return delattr(self.c, attr)

class Context(object):
    """Config/Context Singleton"""
    class __impl:
        def __init__(self):
            self.const = Constants()
            # self.c.destdir = ''       # install default to root by default
            self.destdir = './tmp'    # only for ALPHA
            # the idea is that destdir can be set with --destdir=...

        def setSpecFile(self, pspecfile):
            self.pspecfile = pspecfile
            spec = SpecFile()
            spec.read(pspecfile)
            spec.verify()    # check pspec integrity
            self.spec = spec

            # directory accessor functions
            # here is how it goes
            # x_dir: system wide directory for storing info type x
            # pkg_x_dir: per package directory for storing info type x

        def lib_dir(self):
            return self.destdir + self.const.lib_dir_suffix

        def db_dir(self):
            return self.destdir + self.const.db_dir_suffix

        def archives_dir(self):
            return self.destdir + self.const.archives_dir_suffix
    
        def tmp_dir(self):
            return self.destdir + self.const.tmp_dir_suffix

        def pkg_dir(self):
            packageDir = self.spec.source.name + '-' \
            + self.spec.source.version + '-' + self.spec.source.release

            return self.destdir + self.const.tmp_dir_suffix \
            + '/' + packageDir
   
        def pkg_work_dir(self):
            return self.pkg_dir() + self.const.work_dir_suffix

        def pkg_install_dir(self):
            return self.pkg_dir() + self.const.install_dir_suffix

    __instance = __impl()

    def __init__(self, pspecfile = None):
        if pspecfile != None:
            self.__instance.setSpecFile(pspecfile)

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)


# create a default context WITH NO PSPEC
ctx = Context()
