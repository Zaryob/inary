# -*- coding:utf-8 -*-
#
# Copyright (C) 2005 - 2007, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import os
import sys
import optparse

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.api
import pisi.context as ctx

class autocommand(type):
    def __init__(cls, name, bases, dict):
        super(autocommand, cls).__init__(name, bases, dict)
        Command.cmd.append(cls)
        name = getattr(cls, 'name', None)
        if name is None:
            raise pisi.cli.Error(_('Command lacks name'))
        longname, shortname = name
        def add_cmd(cmd):
            if Command.cmd_dict.has_key(cmd):
                raise pisi.cli.Error(_('Duplicate command %s') % cmd)
            else:
                Command.cmd_dict[cmd] = cls
        add_cmd(longname)
        if shortname:
            add_cmd(shortname)

class Command(object):
    """generic help string for any command"""

    # class variables

    cmd = []
    cmd_dict = {}

    @staticmethod
    def commands_string():
        s = ''
        l = [x.name[0] for x in Command.cmd]
        l.sort()
        for name in l:
            commandcls = Command.cmd_dict[name]
            trans = gettext.translation('pisi', fallback=True)
            summary = trans.ugettext(commandcls.__doc__).split('\n')[0]
            name = commandcls.name[0]
            if commandcls.name[1]:
                name += ' (%s)' % commandcls.name[1]
            s += ' %23s - %s\n' % (name, summary)
        return s

    @staticmethod
    def get_command(cmd, fail=False, args=None):

        if Command.cmd_dict.has_key(cmd):
            return Command.cmd_dict[cmd](args)

        if fail:
            raise pisi.cli.Error(_("Unrecognized command: %s") % cmd)
        else:
            return None

    # instance variabes

    def __init__(self, args = None):
        # now for the real parser
        import pisi
        self.comar = False
        self.parser = optparse.OptionParser(usage=getattr(self, "__doc__"),
                                            version="%prog " + pisi.__version__,
                                            formatter=PisiHelpFormatter())
        self.options()
        self.commonopts()
        (self.options, self.args) = self.parser.parse_args(args)
        if self.args:
            self.args.pop(0)                # exclude command arg

        self.process_opts()

    def commonopts(self):
        '''common options'''
        p = self.parser

        group = optparse.OptionGroup(self.parser, _("general options"))

        group.add_option("-D", "--destdir", action="store", default = None,
                     help = _("Change the system root for PiSi commands"))
        group.add_option("-y", "--yes-all", action="store_true",
                     default=False, help = _("Assume yes in all yes/no queries"))
        group.add_option("-u", "--username", action="store")
        group.add_option("-p", "--password", action="store")
        group.add_option("-L", "--bandwidth-limit", action="store", default = 0,
                     help = _("Keep bandwidth usage under specified KB's"))
        group.add_option("-v", "--verbose", action="store_true",
                     dest="verbose", default=False,
                     help=_("Detailed output"))
        group.add_option("-d", "--debug", action="store_true",
                     default=False, help=_("Show debugging information"))
        group.add_option("-N", "--no-color", action="store_true", default=False,
                     help = _("Suppresses all coloring of PiSi's output"))

        p.add_option_group(group)

        return p

    def options(self):
        """This is a fall back function. If the implementer module provides an
        options function it will be called"""
        pass

    def process_opts(self):
        self.check_auth_info()

        # make destdir absolute
        if self.options.destdir:
            d = str(self.options.destdir)
            if not os.path.exists(d):
                pisi.cli.printu(_('Destination directory %s does not exist. Creating directory.\n') % d)
                os.makedirs(d)
            self.options.destdir = os.path.realpath(d)

    def check_auth_info(self):
        username = self.options.username
        password = self.options.password

        # TODO: We'll get the username, password pair from a configuration
        # file from users home directory. Currently we need user to
        # give it from the user interface.
        #         if not username and not password:
        #             if someauthconfig.username and someauthconfig.password:
        #                 self.authInfo = (someauthconfig.username,
        #                                  someauthconfig.password)
        #                 return
        if username and password:
            self.options.authinfo = (username, password)
            return

        if username and not password:
            from getpass import getpass
            password = getpass(_("Password: "))
            self.options.authinfo = (username, password)
        else:
            self.options.authinfo = None

    def init(self, database = True, write = True):
        """initialize PiSi components"""

        if self.options:
            ui = pisi.cli.CLI(self.options.debug, self.options.verbose)
        else:
            ui = pisi.cli.CLI()

        if write and not os.access(pisi.context.config.packages_dir(), os.W_OK):
            raise pisi.cli.Error(_("You have to be root for this operation."))

        pisi.api.set_userinterface(ui)
        pisi.api.set_options(self.options)
        pisi.api.set_comar(self.comar and not ctx.get_option('ignore_comar'))

    def get_name(self):
        return self.__class__.name

    def format_name(self):
        (name, shortname) = self.get_name()
        if shortname:
            return "%s (%s)" % (name, shortname)
        else:
            return name

    def help(self):
        """print help for the command"""
        trans = gettext.translation('pisi', fallback=True)
        print "%s: %s\n" % (self.format_name(), trans.ugettext(self.__doc__))
        print self.parser.format_option_help()

    def die(self):
        """exit program"""
        #FIXME: not called from anywhere?
        ctx.ui.error(_('Command terminated abnormally.'))
        sys.exit(-1)

class PackageOp(Command):
    """Abstract package operation command"""

    def __init__(self, args):
        super(PackageOp, self).__init__(args)
        self.comar = True

    def options(self, group):
        group.add_option("--ignore-dependency", action="store_true",
                     default=False,
                     help=_("Do not take dependency information into account"))
        group.add_option("--ignore-comar", action="store_true",
                     default=False, help=_("Bypass comar configuration agent"))
        group.add_option("--ignore-safety", action="store_true",
                     default=False, help=_("Bypass safety switch"))
        group.add_option("-n", "--dry-run", action="store_true", default=False,
                     help = _("Do not perform any action, just show what would be done"))

    def init(self, database=True, write=True):
        super(PackageOp, self).init(database, write)

class PisiHelpFormatter(optparse.HelpFormatter):
    def __init__(self,
                 indent_increment=1,
                 max_help_position=32,
                 width=None,
                 short_first=1):
        optparse.HelpFormatter.__init__(
            self, indent_increment, max_help_position, width, short_first)

        self._short_opt_fmt = "%s"
        self._long_opt_fmt = "%s"

    def format_usage(self, usage):
        return _("usage: %s\n") % usage

    def format_heading(self, heading):
        return "%*s%s:\n" % (self.current_indent, "", heading)

    def format_option_strings(self, option):
        """Return a comma-separated list of option strings & metavariables."""
        if option.takes_value():
            short_opts = [self._short_opt_fmt % sopt
                          for sopt in option._short_opts]
            long_opts = [self._long_opt_fmt % lopt
                         for lopt in option._long_opts]
        else:
            short_opts = option._short_opts
            long_opts = option._long_opts

        if long_opts and short_opts:
            opt = "%s [%s]" % (short_opts[0], long_opts[0])
        else:
            opt = long_opts[0] or short_opts[0]

        if option.takes_value():
            opt += " arg"

        return opt

    def format_option(self, option):
        import textwrap
        result = []
        opts = self.option_strings[option]
        opt_width = self.help_position - self.current_indent - 2
        if len(opts) > opt_width:
            opts = "%*s%s\n" % (self.current_indent, "", opts)
            indent_first = self.help_position
        else:                       # start help on same line as opts
            opts = "%*s%-*s  " % (self.current_indent, "", opt_width, opts)
            indent_first = 0
        result.append(opts)
        if option.help:
            help_text = self.expand_default(option)
            help_lines = textwrap.wrap(help_text, self.help_width)
            result.append(": %*s%s\n" % (indent_first, "", help_lines[0]))
            result.extend(["  %*s%s\n" % (self.help_position, "", line)
                           for line in help_lines[1:]])
        elif opts[-1] != "\n":
            result.append("\n")
        return "".join(result)
