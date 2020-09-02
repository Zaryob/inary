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
from gettext import translation
_ = translation('inary', fallback=True).gettext


class Error(Exception):
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


class AlreadyHaveException(Error):
    def __init__(self, url, localfile):
        Error.__init__(
            self, _("URL \"{0}\" already downloaded as \"{1}\"").format(
                url, localfile))
        self.url = url
        self.localfile = localfile


class NoSignatureFound(Error):
    def __init__(self, url):
        Error.__init__(
            self, _("No signature found for \"{}\"").format(url))
        self.url = url


class InvalidSignature(Error):
    def __init__(self, url):
        Error.__init__(
            self, _("GPG Signature is invalid for \"{}\"").format(url))
        self.url = url


class CycleException(Error):
    def __init__(self, cycle):
        self.cycle = cycle

    def __str__(self):
        return _('Encountered cycle {}').format(self.cycle)


class ParserError(Error):
    pass


class PostOpsError(Error):
    pass


class NotfoundError(Error):
    pass
