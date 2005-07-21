#!/usr/bin/python
# -*- coding: utf-8 -*-

from actionglobals import glb

env = glb.env
dirs = glb.dirs
flags = glb.flags

def pkgDIR():
    return env.pkg_dir

def workDIR():
    return env.work_dir

def installDIR():
    return env.install_dir

def srcNAME():
    return env.src_name

def srcVERSION():
    return env.src_version

def srcRELEASE():
    return env.src_release

def HOST():
    return flags.host

def CFLAGS():
    return flags.cflags

def CXXFLAGS():
    return flags.cxxflags

def LDFLAGS():
    return flags.ldflags
