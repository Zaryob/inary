# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# pisi.cli package version
__version__ = "0.1"

import sys

import pisi
import pisi.context as ctx
from pisi.ui import UI
from pisi.cli.colors import colorize


class Error(pisi.Error):
    pass


class Exception(pisi.Exception):
    pass


class CLI(UI):
    "Command Line Interface"

    def __init__(self, show_debug = False, show_verbose = False):
        super(CLI, self).__init__(show_debug, show_verbose)

    def output(self, str):
        sys.stdout.write(str)
        sys.stdout.flush()

    def info(self, msg, verbose = False):
        # TODO: need to look at more kinds of info messages
        # let's cheat from KDE :)
        if verbose and self.show_verbose:
            self.output(msg + '\n')
        elif not verbose:
            self.output(msg + '\n')

    def warning(self,msg):
        self.output(colorize('Warning:' + msg + '\n', 'purple'))

    def error(self,msg):
        self.output(colorize('Error:' + msg + '\n', 'red'))

    def action(self,msg):
        #TODO: this seems quite redundant?
        self.output(colorize(msg + '\n', 'green'))

    def choose(self, msg, opts):
        print msg
        for i in range(0,len(opts)):
            print i + 1, opts(i)
        while True:
            s = raw_input(msg + colorize('1-%d' % len(opts), 'red'))
            try:
                opt = int(s)
                if 1 <= opt and opt <= len(opts):
                    return opts(opt-1)
            except (Exception,e):
                pass
        
    def confirm(self, msg):
        if ctx.config.options and ctx.config.options.yes_all:
            return True
        while True:
            s = raw_input(msg + colorize('(yes/no)', 'red'))
            if s.startswith('y') or s.startswith('Y'):
                return True
            if s.startswith('n') or s.startswith('N'):
                return False

    def display_progress(self, pd):
        out = '\r%-30.30s %3d%% %12.2f %s' % \
            (pd['filename'], pd['percent'], pd['rate'], pd['symbol'])
        self.output(out)

