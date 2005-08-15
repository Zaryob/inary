# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# generic user interface

# Authors:  Eray Ozkural <eray@uludag.org.tr>
#           Murat Eren <meren@uludag.org.tr>

import sys

from pisi.colors import colorize
from pisi.config import config

def register(_impl):
    """ Register a UI implementation"""
    ui = _impl

# default UI implementation
class CLI:
    def __init__(self, debuggy = False, verbose = False):
        self.show_debug = debuggy
        self.show_verbose = verbose

    def set_verbose(self, flag):
        self.show_verbose = flag

    def set_debug(self, flag):
        self.show_debug = flag

    def info(self, msg, verbose = False):
        if verbose and self.show_verbose:
            sys.stdout.write(colorize(msg, 'blue'))
        elif not verbose:
            sys.stdout.write(colorize(msg, 'blue'))
        sys.stdout.flush()

    def debug(self, msg):
        if self.show_debug:
            sys.stdout.write(msg)
            sys.stdout.flush()

    def warning(self,msg):
        sys.stdout.write(colorize('Warning:' + msg, 'purple'))
        sys.stdout.flush()

    def error(self,msg):
        sys.stdout.write(colorize('Error:' + msg, 'red'))
        sys.stdout.flush()

    def action(self,msg):
        sys.stdout.write(colorize(msg, 'green'))
        sys.stdout.flush()

    def confirm(self, msg):
        from pisi.config import config
        if config.options and config.options.yes_all:
            return True
        while True:
            s = raw_input(msg + colorize('(yes/no)', 'red'))
            if s.startswith('y') or s.startswith('Y'):
                return True
            if s.startswith('n') or s.startswith('N'):
                return False

    class Progress:
        def __init__(self, totalsize):
            self.totalsize = totalsize
            self.percent = 0

        def update(self, size):
            if not self.totalsize:
                return 100

            percent = (size * 100) / self.totalsize
            if percent and self.percent is not percent:
                self.percent = percent
                return percent
            else:
                return 0

    def display_progress(self, pd):
        out = '\r%-30.30s %3d%% %12.2f %s' % \
            (pd['filename'], pd['percent'], pd['rate'], pd['symbol'])
        self.info(out)

# default UI is CLI
ui = None
#CLI()
