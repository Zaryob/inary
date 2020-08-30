# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2020, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
class Error(BaseException):
    """Class of exceptions that lead to program termination"""
    pass


class AnotherInstanceError(Error):
    pass


class PrivilegeError(Error):
    pass

# Error Classes
class FileError(Error):
    def __init__(self, value=''):
        Error.__init__(self, value)
        self.value = value


class ArgumentError(Error):
    def __init__(self, value=''):
        Error.__init__(self, value)
        self.value = value

class FilePermissionDeniedError(Error):
    pass

# Error Classes
class FileError(Error):
    def __init__(self, value=''):
        Error.__init__(self, value)
        self.value = value


class ArgumentError(Error):
    def __init__(self, value=''):
        Error.__init__(self, value)
        self.value = value
