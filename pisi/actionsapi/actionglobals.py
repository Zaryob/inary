# -*- coding: utf-8 -*-

# standard python modules
import os

# pisi modules
import pisi.config
import pisi.constants


# Set individual information, that are generally needed for actions
# api.

class Env:
    """General environment variables used in actions API"""
    pkg_dir = os.getenv('PKG_DIR')
    work_dir = os.getenv('WORK_DIR')
    install_dir = os.getenv('INSTALL_DIR')
    src_name = os.getenv('SRC_NAME')
    src_version = os.getenv('SRC_VERSION')
    src_release = os.getenv('SRC_RELEASE')

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
    conf = pisi.config.config.conf
    host = conf.build.host
    cflags = conf.build.cflags
    cxxflags = conf.build.cflags

class ActionGlobals(pisi.config.Config):
    const = pisi.constants.const
    env = Env()
    dirs = Dirs()
    flags = Flags()

glb = ActionGlobals()
