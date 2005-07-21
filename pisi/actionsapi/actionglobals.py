# -*- coding: utf-8 -*-

# standard python modules
from os import getenv, environ

# pisi modules
import pisi.config
import pisi.constants


# Set individual information, that are generally needed for actions
# api.

class Env(object):
    """General environment variables used in actions API"""
    def __init__(self):
        self.__vars = {
            "pkg_dir": "PKG_DIR",
            "work_dir": "WORK_DIR",
            "install_dir": "INSTALL_DIR",
            "src_name": "SRC_NAME",
            "src_version": "SRC_VERSION",
            "src_release": "SRC_RELEASE"
            }

    def __getattr__(self, attr):

        # Using environment variables is somewhat tricky. Each time
        # you need them you need to check for their value.
        if self.__vars.has_key(attr):
            return getenv(self.__vars[attr])
        else:
            return None



class Dirs:
    """General directories used in actions API."""
    # TODO: Eventually we should consider getting these from a/the
    # configuration file
    doc = "usr/share/doc"
    sbin = "usr/sbin"
    man = "usr/share/man"
    info = "usr/share/info"
    data = "usr/share"
    conf = "etc"
    localstate = "var/lib"
    defaultprefix = "usr"

class Flags:
    """General flags used in actions API"""
    values = pisi.config.config.values
    environ["HOST"] = host = values.build.host
    environ["CFLAGS"] = cflags = values.build.cflags
    environ["CXXLAGS"] = cxxflags = values.build.cflags

class ActionGlobals(pisi.config.Config):
    const = pisi.constants.const
    env = Env()
    dirs = Dirs()
    flags = Flags()

glb = ActionGlobals()
