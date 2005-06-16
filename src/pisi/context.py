# -*- coding: utf-8 -*-
# PISI configuration (static and dynamic)

from specfile import SpecFile

class Constants:
    """Pisi constants"""
    class __const:
	"""Constant members implementation"""
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

    c = __const()

    def __init__(self):
	self.c.lib_dir_suffix = "/var/lib/pisi"
	self.c.db_dir_suffix = "/var/db/pisi"
	self.c.archives_dir_suffix = "/var/cache/pisi/archives"
	self.c.tmp_dir_suffix =  "/var/tmp/pisi"

	# directory suffixes for build
	self.c.build_work_dir_suffix = "/work"
	self.c.build_install_dir_suffix  = "/install"

    def __getattr__(self, attr):
 	return getattr(self.c, attr)

    def __setattr__(self, attr, value):
 	return setattr(self.c, attr, value)


class Context(object):
    """Config/Context Singleton"""
    class __impl:
	def __init__(self):
	    self.const = Constants()
	    # self.c.destdir = ''       # install default to root by default
	    self.const.destdir = './tmp'    # only for ALPHA
	    # the idea is that destdir can be set with --destdir=...

	def _specFile(self, pspecfile):
	    self.pspecfile = pspecfile
	    spec = SpecFile()
	    spec.read(pspecfile)
	    spec.verify()	# check pspec integrity

	    self.spec = spec

	def lib_dir(self):
	    return self.const.destdir + self.const.lib_dir_suffix

	def db_dir(self):
	    return self.const.destdir + self.const.db_dir_suffix

	def archives_dir(self):
	    return self.const.destdir + self.const.archives_dir_suffix
	
	def tmp_dir(self):
	    return self.const.destdir + self.const.tmp_dir_suffix
	
	def build_work_dir(self):
	    packageDir = self.spec.source.name + '-' \
		+ self.spec.source.version + '-' + self.spec.source.release

	    return self.const.destdir + self.const.tmp_dir_suffix \
		+ '/' + packageDir + self.const.build_work_dir_suffix

	def build_install_dir(self):
	    packageDir = self.spec.source.name + '-' \
		+ self.spec.source.version + '-' + self.spec.source.release

	    return self.const.destdir + self.const.tmp_dir_suffix \
		+ '/' + packageDir + self.const.build_install_dir_suffix

    __instance = __impl()

    def __init__(self, pspecfile):
	self.__instance._specFile(pspecfile)

    def __getattr__(self, attr):
 	return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
 	return setattr(self.__instance, attr, value)
