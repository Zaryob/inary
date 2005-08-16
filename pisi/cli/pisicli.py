# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import sys
from optparse import OptionParser

import pisi
from pisi.uri import URI
from pisi.cli.common import *
from pisi.cli.commands import *

class ParserError(Exception):
    pass

class Parser(OptionParser):
    def __init__(self, version):
        OptionParser.__init__(self, usage=usage_text, version=version)

    def error(self, msg):
        raise ParserError, msg

class PisiCLI(object):

    def __init__(self):
        # first construct a parser for common options
        # this is really dummy
        self.parser = Parser(version="%prog " + pisi.__version__)
        #self.parser.allow_interspersed_args = False
        self.parser = commonopts(self.parser)

        cmd = ""
        try:
            (options, args) = self.parser.parse_args()
            if len(args)==0:
                self.die()
            cmd = args[0]
            
        except IndexError:
            self.die()
        except ParserError:
            # fully expected :) let's see if we got an argument
            if len(self.parser.rargs)==0:
                self.die()
            cmd = self.parser.rargs[0]

        self.command = Command.get_command(cmd)
        if not self.command:
            print "Unrecognized command: ", cmd
            self.die()

    def die(self):
        self.parser.print_help()
        sys.exit(1)

    def run_command(self):
        self.command.run()
