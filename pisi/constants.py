# PISI constants. 
# If you have a "magic" constant value this is where it should be
# defined.

# Author: Baris Metin <baris@uludag.org.tr

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
    "Pisi Constants Singleton"

    __c = _constant()

    def __init__(self):
        # Constants for metadata
        #TODO: These two will be defined in a configuration file.
        self.__c.distribution = "Pardus"
        self.__c.distributionRelease = "0.1"

        # directories
        self.__c.lib_dir_suffix = "/var/lib/pisi"
        self.__c.db_dir_suffix = "/var/db/pisi"
        self.__c.archives_dir_suffix = "/var/cache/pisi/archives"
        self.__c.tmp_dir_suffix =  "/var/tmp/pisi"

        # directory suffixes for build
        self.__c.work_dir_suffix = "/work"
        self.__c.install_dir_suffix  = "/install"

        # file/directory names
        self.__c.actions_file = "actions.py"
        self.__c.files_dir = "files"
        self.__c.comar_dir = "comar"
        self.__c.files_xml = "files.xml"
        self.__c.metadata_xml = "metadata.xml"

        # functions in actions_file
        self.__c.setup_func = "setup"
        self.__c.build_func = "build"
        self.__c.install_func = "install"

    def __getattr__(self, attr):
        return getattr(self.__c, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__c, attr, value)

    def __delattr__(self, attr):
        return delattr(self.__c, attr)

# singleton for easy access here
const = Constants()
