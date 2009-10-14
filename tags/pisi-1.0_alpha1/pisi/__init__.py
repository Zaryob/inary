# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# PiSi version

__version__ = "0.3"

__all__ = [ 'api', 'packagedb', 'installdb' ]

class Error(Exception):
    """Class of exceptions that lead to program termination"""
    pass

class Exception(Exception):
    """Class of exceptions that must be caught and handled within PISI"""
    pass

# FIXME: can't do this due to name clashes in config and other singletons booo
#from pisi.api import *
