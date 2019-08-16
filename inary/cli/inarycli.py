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
#

import sys
import optparse
import sys

import gettext

__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary
import inary.errors

import inary.cli
import inary.cli.command as command
import inary.cli.addrepo
import inary.cli.blame
import inary.cli.build
import inary.cli.check
import inary.cli.configurepending
import inary.cli.deletecache
import inary.cli.delta
import inary.cli.emerge
import inary.cli.emergeup
import inary.cli.fetch
import inary.cli.graph
import inary.cli.index
import inary.cli.info
import inary.cli.install
import inary.cli.history
import inary.cli.listnewest
import inary.cli.listavailable
import inary.cli.listcomponents
import inary.cli.listinstalled
import inary.cli.listorphaned
import inary.cli.listpending
import inary.cli.listrepo
import inary.cli.listsources
import inary.cli.listupgrades
import inary.cli.rebuilddb
import inary.cli.remove
import inary.cli.removerepo
import inary.cli.removeorphaned
import inary.cli.enablerepo
import inary.cli.disablerepo
import inary.cli.searchfile
import inary.cli.search
import inary.cli.updaterepo
import inary.cli.upgrade

# FIXME: why does this has to be imported last
import inary.cli.help


class ParserError(inary.errors.Exception):
    pass


class PreParser(optparse.OptionParser):
    """consumes any options, and finds arguments from command line"""

    def __init__(self, version):
        optparse.OptionParser.__init__(self, usage=inary.cli.help.usage_text, version=version)

    def error(self, msg):
        raise ParserError(msg)

    def parse_args(self, args=None):
        self.opts = []
        self.rargs = self._get_args(args)
        self._process_args()
        return self.opts, self.args

    def _process_args(self):
        args = []
        rargs = self.rargs
        if not self.allow_interspersed_args:
            first_arg = False
        while rargs:
            arg = rargs[0]

            def option():
                if not self.allow_interspersed_args and first_arg:
                    self.error(_('Options must precede non-option arguments.'))
                arg = rargs[0]
                if arg.startswith('--'):
                    self.opts.append(arg[2:])
                else:
                    self.opts.append(arg[1:])
                del rargs[0]
                return

            # We handle bare "--" explicitly, and bare "-" is handled by the
            # standard arg handler since the short arg case ensures that the
            # len of the opt string is greater than 1.
            if arg == "--":
                del rargs[0]
                break
            elif arg[0:2] == "--":
                # process a single long option (possibly with value(s))
                option()
            elif arg[:1] == "-" and len(arg) > 1:
                # process a cluster of short options (possibly with
                # value(s) for the last one only)
                option()
            else:  # then it must be an argument
                args.append(arg)
                del rargs[0]
        self.args = args


class InaryCLI(object):

    def __init__(self, orig_args=None):
        # first construct a parser for common options
        # this is really dummy

        self.parser = PreParser(version="%prog " + inary.__version__)
        try:
            opts, args = self.parser.parse_args(args=orig_args)
            if len(args) == 0:  # more explicit than using IndexError
                if 'version' in opts:
                    self.parser.print_version()
                    sys.exit(0)
                elif 'help' in opts or 'h' in opts:
                    self.die()
                raise inary.cli.Error(_('No command given.'))
            cmd_name = args[0]
        except ParserError:
            raise inary.cli.Error(_('Command line parsing error.'))

        self.command = command.Command.get_command(cmd_name, args=orig_args)
        if not self.command:
            raise inary.cli.Error(_("Unrecognized command: {}").format(cmd_name))

    def die(self):
        inary.cli.printu('\n' + self.parser.format_help())
        sys.exit(1)

    def run_command(self):
        self.command.run()
