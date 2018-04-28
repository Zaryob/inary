# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

"ctype analyzer"

class CTypes:
    def __init__(self, fname):
        """Analyze ctypes. Find libraries and load"""
        self.library_handle ={}
        self.library_names = {}
        self.name = name
        try:
            import ctypes
            import ctypes.util
        except ImportError:
            try:
                ctypes.cdll
            except:
                raise Exception(_("Module \"ctypes\" can not import"))


    def find_library(self):
        fname = self.library_names.get(name)
        if fname is None:
            fname = ctypes.util.find_library(name)
            if fname is None:
                fname = False
            self.library_names[name] = fname

        if fname is False:
            return None
        return fname

    def LoadLibrary(name):
        handle = self.library_handle.get(name)
        if handle is None:
            handle = ctypes.CDLL(name, use_errno=True)
            self.library_handles[name] = handle
        return handle
