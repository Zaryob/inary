# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2020, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# Standart Python Modules
import os
import time
import pickle

# Inary Modules
import inary.context as ctx
import inary.util as util

# lower borks for international locales. What we want is ascii lower.
lower_map = str.maketrans(util.ascii_uppercase, util.ascii_lowercase)


class Singleton(object):
    _the_instances = {}

    def __new__(type):
        if type.__name__ not in Singleton._the_instances:
            Singleton._the_instances[type.__name__] = object.__new__(type)
        return Singleton._the_instances[type.__name__]

    def _instance(self):
        return self._the_instances[type(self).__name__]

    def _delete(self):
        # FIXME: After invalidate, previously initialized db object becomes
        ctx.ui.debug(
            "LazyDB: {0} invalidated.".format(
                self.__class__.__name__))
        del self._the_instances[type(self).__name__]


class LazyDB(Singleton):
    cache_version = "1.0"

    def __init__(self, cacheable=False, cachedir=None):
        if "initialized" not in self.__dict__:
            self.initialized = False
        self.cacheable = cacheable
        self.cachedir = cachedir

    def is_initialized(self):
        return self.initialized

    def __cache_file(self):
        return util.join_path(ctx.config.cache_root_dir(),
                              "{}.cache".format(self.__class__.__name__.translate(lower_map)))

    def __cache_version_file(self):
        return "{}.version".format(self.__cache_file())

    def __cache_file_version(self):
        try:
            return open(self.__cache_version_file()).read().strip()
        except IOError:
            return "2.2"

    def cache_save(self):
        if os.access(ctx.config.cache_root_dir(), os.W_OK) and self.cacheable:
            with open(self.__cache_version_file(), "w") as f:
                f.write(LazyDB.cache_version)
                f.flush()
                os.fsync(f.fileno())
            pickle.dump(self._instance().__dict__,
                        open(self.__cache_file(), 'wb'), 1)

            ctx.ui.debug("LazyDB: {0} cached.".format(self.__class__.__name__))

    def cache_valid(self):
        if not self.cachedir:
            return True
        if not os.path.exists(self.cachedir):
            return False
        if self.__cache_file_version() != LazyDB.cache_version:
            return False

        cache_modified = os.stat(self.__cache_file()).st_mtime
        cache_dir_modified = os.stat(self.cachedir).st_mtime
        return cache_modified > cache_dir_modified

    def cache_load(self):
        if os.path.exists(self.__cache_file()) and self.cache_valid():
            try:
                self._instance().__dict__ = pickle.load(open(self.__cache_file(), 'rb'))
                return True
            except (pickle.UnpicklingError, EOFError):
                if os.access(ctx.config.cache_root_dir(), os.W_OK):
                    os.unlink(self.__cache_file())
                return False
        return False

    def cache_flush(self):
        if os.path.exists(self.__cache_file()):
            os.unlink(self.__cache_file())
            ctx.ui.debug("LazyDB: {0} cached.".format(self.__class__.__name__))

    def invalidate(self):
        self._delete()

    def cache_regenerate(self):
        try:
            self.this_attr_does_not_exist()
        except AttributeError:
            pass

    def __init(self):
        if not self.cache_load():
            self.init()

    def __getattr__(self, attr):
        if not attr == "__setstate__" and not self.initialized:
            start = time.time()
            self.__init()
            end = time.time()
            ctx.ui.debug(
                "{0} initialized in {1}.".format(
                    self.__class__.__name__,
                    end - start))
            self.initialized = True

        if attr not in self.__dict__:
            raise AttributeError(attr)

        return self.__dict__[attr]
