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
#
# generic user interface
#

(installed, upgraded, removed, installing, removing, configuring, configured, extracting,
 downloading, packagestogo, updatingrepo, cached, desktopfile, fetching, fetched) = list(range(15))


class UI(object):
    """Abstract class for UI operations, derive from this."""

    class Progress:
        def __init__(self, totalsize, existsize=0):
            self.totalsize = totalsize
            try:
                self.percent = (existsize * 100) / totalsize
            except ArithmeticError:
                self.percent = 0

        def update(self, size):
            if not self.totalsize:
                return 100
            try:
                self.percent = (size * 100) / self.totalsize
            except ArithmeticError:
                self.percent = 0
            return self.percent

    def __init__(self, debuggy=False, verbose=False):
        self.show_debug = debuggy
        self.show_verbose = verbose
        self.errors = 0
        self.warnings = 0

    def close(self):
        """cleanup stuff here"""
        pass

    def set_verbose(self, flag):
        self.show_verbose = flag

    def set_debug(self, flag):
        self.show_debug = flag

    def info(self, msg, verbose=False, noln=False, color='default'):
        """give an informative message"""
        pass

    def ack(self, msg):
        """inform the user of an important event and wait for acknowledgement"""
        pass

    def debug(self, msg, color='normal'):
        """show debugging info"""
        if self.show_debug:
            self.info(str('DEBUG: ' + msg), color)

    def warning(self, msg):
        """warn the user"""
        pass

    def error(self, msg):
        """inform a (possibly fatal) error"""
        pass

    # FIXME: merge this with info, this just means "important message"
    def action(self, msg):
        """uh?"""
        pass

    def choose(self, msg, list):
        """ask the user to choose from a list of alternatives"""
        pass

    def confirm(self, msg, invert=False):
        """ask the user to confirm question"""
        pass

    def display_progress(self, **ka):
        """display progress"""
        pass

    def status(self, msg=None, push_screen=True):
        """set status, if not given clear it"""
        pass

    def notify(self, event, logging=True, **keywords):
        """notify UI of a significant event"""
        pass
