# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE (Licensed with GPLv2)
# More details about GPLv2, please read the COPYING.OLD file.
#
# Copyright (C) 2016 - 2019, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# Please read the COPYING file.

# FIXME: Exception shadows builtin Exception. This is no good.
class Exception(Exception):
    """Class of exceptions that must be caught and handled within INARY"""

    def __str__(self):
        s = ''
        for x in self.args:
            if s != '':
                s += '\n'
            s += str(x)
        return str(s)


class Error(Exception):
    """Class of exceptions that lead to program termination"""
    pass


class AnotherInstanceError(Exception):
    pass


class PrivilegeError(Exception):
    pass
