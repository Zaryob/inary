#!/usr/bin/python
# -*- coding: utf-8 -*-

# stadard python modules
import os
import time
from tempfile import mkstemp, mkdtemp

def sleep(sleep_time = 5):
    time.sleep(sleep_time)

def createTmpFile():
    handle, path = mkstemp()
    return path

def createTmpDir():
    path = mkdtemp()
    return path

def chmod(filename, mode = 0755):
    os.chmod(filename, mode)

def unlink(filename):
    os.unlink(filename)

def makedirs(directoryName):
    try:
        os.makedirs(directoryName)
    except OSError:
        pass
