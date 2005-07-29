#!/usr/bin/python
# -*- coding: utf-8 -*-

# Standart Python Modules
import os.path

# ActionsAPI Modules
from variables import glb

env = glb.env
dirs = glb.dirs
flags = glb.flags

def pkgDIR():
    return env.pkg_dir

def workDIR():
    return env.work_dir

def installDIR():
    return env.install_dir

def infoDIR():
    return os.path.join(installDIR(), dirs.info)

def manDIR():
    return os.path.join(installDIR(), dirs.man)
    
def srcNAME():
    return env.src_name

def srcVERSION():
    return env.src_version

def srcRELEASE():
    return env.src_release

def srcTAG():
    return env.src_name + '-' + env.src_version + '-' + env.src_release

def srcDIR():
    return env.src_name + '-' + env.src_version
        
def HOST():
    return flags.host

def CFLAGS():
    return flags.cflags

def CXXFLAGS():
    return flags.cxxflags

def LDFLAGS():
    return flags.ldflags

def getBinutilsInfo(needed):
    return "%s-%s" % (HOST(), needed)

def AR():
    return getBinutilsInfo("ar")

def AS():
    return getBinutilsInfo("as")

def CC():
    return getBinutilsInfo("gcc")

def CXX():
    return getBinutilsInfo("g++")

def LD():
    return getBinutilsInfo("ld")

def NM():
    return getBinutilsInfo("nm")

def RANLIB():
    return getBinutilsInfo("ranlib")

def F77():
    return getBinutilsInfo("f77")

def GCJ():
    return getBinutilsInfo("gcj")

