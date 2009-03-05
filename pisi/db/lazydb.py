# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2009, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import os
import cPickle
import time
import pisi.context as ctx

class Singleton(object):
    def __new__(type):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance

class LazyDB(Singleton):
    def __init__(self, cacheable=False):
        if not self.__dict__.has_key("initialized"):
            self.initialized = False
        self.cacheable = cacheable

    def is_initialized(self):
        return self.initialized

    def cache_save(self):
        if os.access("/var/cache/pisi", os.W_OK) and self.cacheable:
            cPickle.dump(self.__class__._the_instance.__dict__,
                         file('/var/cache/pisi/%s.cache' % self.__class__.__name__.lower(), 'wb'), 1)

    def cache_load(self):
        if os.path.exists("/var/cache/pisi/%s.cache" % self.__class__.__name__.lower()):
            self.__class__._the_instance.__dict__ = cPickle.load(file('/var/cache/pisi/%s.cache' % self.__class__.__name__.lower(), 'rb'))
            return True
        return False

    def cache_flush(self):
        cache_file = "/var/cache/pisi/%s.cache" % self.__class__.__name__.lower()
        if os.path.exists(cache_file):
            os.unlink(cache_file)

    def reload(self):
        self.cache_flush()
        self.__init()

    def close(self):
        self.cache_save()

    def __init(self):
        if not self.cache_load():
            self.init()
            self.cache_save()

    def __getattr__(self, attr):
        if not attr == "__setstate__" and not self.initialized:
            start = time.time()
            self.__init()
            end = time.time()
            ctx.ui.debug("%s initialized in %s." % (self.__class__.__name__, end - start))
            self.initialized = True

        if not self.__dict__.has_key(attr):
            raise AttributeError, attr

        return self.__dict__[attr]
