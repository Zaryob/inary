#!/usr/bin/python
# -*- coding: utf-8 -*-

# stadard python modules
import os
import time
import glob
import shutil
from tempfile import mkstemp, mkdtemp

def sleep(seconds = 5):
    time.sleep(seconds)

def createTmpFile():
    handle, path = mkstemp()
    return path

def createTmpDir():
    path = mkdtemp()
    return path

def chmod(filename, mode = 0755):
    for file in glob.glob(filename):
        os.chmod(file, mode)

def unlink(filename):
    os.unlink(filename)

def makedirs(directoryName):
    try:
        os.makedirs(directoryName)
    except OSError:
        pass

def touch(filename):
    for file in glob.glob(filename):
        os.utime(file, None)

def changeDir(directoryName = ''):
    current = os.getcwd()
    if directoryName:
        os.chdir(directoryName)
    else:
        os.chdir(os.path.dirname(current))

def ls(directory):
    return os.listdir(directory)

def move(source, destination):
    shutil.move(source, destination)

def export(key, value):
    os.environ[key] = value
