#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from tempfile import mkstemp, mkdtemp

def sleep( sleep_time = 5 ):
    time.sleep( sleep_time )

def createTmpFile():
    handle, path = mkstemp()
    return path

def createTmpDir():
    path = mkdtemp()
    return path

