# -*- coding: utf-8 -*-
#
# Copyright (C) 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import sys
import glob
import os
import threading

import gettext
__trans = gettext.translation("inary", fallback=True)
_ = __trans.gettext

import ctypes
from ctypes import c_char_p, c_int, c_size_t, c_void_p
import ctypes.util

class MagicException(Exception):
    def __init__(self, message):
        super(MagicException, self).__init__(message)
        self.message = message

libmagic = None
dll = ctypes.util.find_library('magic') or ctypes.util.find_library('magic1') or ctypes.util.find_library('cygmagic-1')

if dll:
    libmagic = ctypes.CDLL(dll)

if not libmagic or not libmagic._name:
    magic_dlls = {'darwin': ['/opt/local/lib/libmagic.dylib',
                                  '/usr/local/lib/libmagic.dylib',
                                  glob.glob('/usr/local/Cellar/libmagic/*/lib/libmagic.dylib')],
                       'win32': ['magic1.dll','cygmagic-1.dll'],
                       'linux': ['libmagic.so.1'],
                      }

    if sys.platform.startswith('linux'):
        platform = 'linux'
    else:
        platform = sys.platform

    for dll in magic_dlls.get(platform, []):
        try:
            libmagic = ctypes.CDLL(dll)
            break
        except OSError:
            pass
#Magic Flags from libmagic.so

MAGIC_CONTINUE = 0x000020
MAGIC_COMPRESS = 0x000004
MAGIC_NONE = 0x000000
MAGIC_MIME = 0x000010
MAGIC_MIME_ENCODING = 0x000400

_instances = {}

# Magic function
magic_t = ctypes.c_void_p

#Error Checking Function
def errorcheck(result, func, args):
    if result is None:
        err = magic_error(args[0])
        raise Exception(err)
    elif result is -1:
        err = magic_error(args[0])
        raise Exception(err)
    else:
        return result

# Declarations
magic_file = libmagic.magic_file
magic_file.restype = c_char_p
magic_file.argtypes = [magic_t, c_char_p]
magic_file.errcheck = errorcheck

magic_open = libmagic.magic_open
magic_open.restype = magic_t
magic_open.argtypes = [c_int]

magic_close = libmagic.magic_close
magic_close.restype = None
magic_close.argtypes = [magic_t]

magic_buffer = libmagic.magic_buffer
magic_buffer.restype = c_char_p
magic_buffer.argtypes = [magic_t, c_void_p, c_size_t]
magic_buffer.errcheck = errorcheck

magic_load = libmagic.magic_load
magic_load.restype = c_int
magic_load.argtypes = [magic_t, c_char_p]
magic_load.errcheck = errorcheck

#Standart Functions
def _get_wrapper(mime):
    i = _instances.get(mime)
    if i is None:
        i = _instances[mime] = Magic(mime=mime)
    return i

def file_type(data, mime=False):
    m = _get_wrapper(mime)
    return m.get_file_type(data)

# Magic Class
class Magic:

    def __init__(self, mime=False, magic_file=None, mime_encoding=False,
                 keep_going=False, uncompress=False):

        self.flags = MAGIC_NONE
        if mime:
            self.flags |= MAGIC_MIME
        if mime_encoding:
            self.flags |= MAGIC_MIME_ENCODING
        if keep_going:
            self.flags |= MAGIC_CONTINUE

        if uncompress:
            self.flags |= MAGIC_COMPRESS

        self.cookie = magic_open(self.flags)
        self.lock = threading.Lock()

        magic_load(self.cookie, magic_file)

    def get_file_type(self, data):
        # If given argument is a file load with magic_file
        # If given argument is a buffer load with magic_buffer
        try:
            if os.path.isfile(data):
                open(data)
                with self.lock:
                    return magic_file(self.cookie, data.encode('utf-8')).decode('utf-8')
            else:
                with self.lock:
                    if type(data) == str and str != bytes:
                        buf = data.encode('utf-8', errors='replace')
                    return magic_buffer(self.cookie, data, len(data)).decode('utf-8')
        except MagicException as err:
            raise(_("Can't load file or buffer {}").format(err))

    def __del__(self):
        if self.cookie and magic_close:
            magic_close(self.cookie)
            self.cookie = None
