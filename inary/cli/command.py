# -*- coding:utf-8 -*-
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

# Standart Python Modules
import os
import sys
import optparse

# Inary Modules
import inary.settings
import inary.util as util
import inary.context as ctx

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class autocommand(type):
    def __init__(cls, name, bases, dict):
        super(autocommand, cls).__init__(name, bases, dict)
        Command.cmd.append(cls)
        name = getattr(cls, 'name', None)
        if name is None:
            raise inary.cli.Error(_('Command lacks name.'))
        longname, shortname = name

        def add_cmd(cmd):
            if cmd in Command.cmd_dict:
                raise inary.cli.Error(
                    _('Duplicate command \'{}\'').format(cmd))
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
        l = sorted([x.name[0] for x in Command.cmd])
        for name in l:
            commandcls = Command.cmd_dict[name]
            trans = gettext.translation('inary', fallback=True)
            summary = trans.gettext(commandcls.__doc__).split('\n')[0]
            name = commandcls.name[0]
            if commandcls.name[1]:
                name += ' ({})'.format(commandcls.name[1])
            s += util.colorize(' %23s ' % name, 'blue') + '- %s\n' % summary
        return s

    @staticmethod
    def get_command(cmd, fail=False, args=None):

        if cmd in Command.cmd_dict:
            return Command.cmd_dict[cmd](args)

        if fail:
            raise inary.cli.Error(
                _("Unrecognized command: \'{}\'").format(cmd))
        else:
            return None

    # instance variabes

    def __init__(self, args=None):
        # now for the real parser
        import inary
        self.parser = optparse.OptionParser(usage=getattr(self, "__doc__"),
                                            version="%prog " + inary.__version__,
                                            formatter=InaryHelpFormatter())
        self.options()
        self.commonopts()
        (self.options, self.args) = self.parser.parse_args(args)
        if self.args:
            self.args.pop(0)  # exclude command arg

        self.process_opts()

    def commonopts(self):
        """common options"""
        p = self.parser

        group = optparse.OptionGroup(self.parser, _("general options"))

        group.add_option("-D", "--destdir", action="store", default=None,
                         help=_("Change the system root for INARY commands."))
        group.add_option("-y", "--yes-all", action="store_true",
                         default=False, help=_("Assume yes in all yes/no queries."))
        group.add_option("-u", "--username", action="store")
        group.add_option("-p", "--password", action="store")
        group.add_option("-L", "--bandwidth-limit", action="store", default=0,
                         help=_("Keep bandwidth usage under specified KB's."))
        group.add_option("-v", "--verbose", action="store_true",
                         dest="verbose", default=False,
                         help=_("Detailed output"))
        group.add_option("-d", "--debug", action="store_true",
                         default=False, help=_("Show debugging information."))
        group.add_option("-N", "--no-color", action="store_true", default=False,
                         help=_("Suppresses all coloring of INARY's output."))

        p.add_option_group(group)

        return p

    def options(self):
        """This is a fall back function. If the implementer module provides an
        options function it will be called"""
        pass

    def process_opts(self):
        # make destdir absolute
        if self.options.destdir:
            d = str(self.options.destdir)
            if not os.path.exists(d):
                inary.cli.printu(
                    _('Destination directory \"{}\" does not exist. Creating directory.\n').format(d))
                os.makedirs(d)
            self.options.destdir = os.path.realpath(d)

    def init(self, database=True, write=True, locked=False):
        """initialize INARY components"""
        if self.options:
            ui = inary.cli.CLI(self.options.debug, self.options.verbose)
        else:
            ui = inary.cli.CLI()

        if (write and not os.access(inary.context.config.packages_dir(), os.W_OK) or
                ('sf' == self.get_name() or 'cp' == self.get_name() and not os.access(
                    os.path.join(ctx.config.info_dir(), ctx.const.files_db), os.W_OK))):
            raise inary.cli.Error(_("You have to be root for this operation."))

        inary.settings.set_userinterface(ui)
        inary.settings.set_options(self.options)

    def get_name(self):
        return self.__class__.name

    def format_name(self):
        (name, shortname) = self.get_name()
        if shortname:
            return "{0} ({1})".format(name, shortname)
        else:
            return name

    def help(self):
        """print help for the command"""
        trans = gettext.translation('inary', fallback=True)
        print(
            "{0}: {1}".format(
                self.format_name(),
                trans.gettext(
                    self.__doc__)))
        print(self.parser.format_option_help())

    @staticmethod
    def die():
        """exit program"""
        ctx.ui.error(_('Command terminated abnormally.'))
        # util.noecho(False)
        # FixME
        sys.exit(-1)


class PackageOp(Command):
    """Abstract package operation command"""

    def __init__(self, args):
        super(PackageOp, self).__init__(args)

    def options(self, group):
        group.add_option("--ignore-dependency", action="store_true",
                         default=False,
                         help=_("Do not take dependency information into account."))
        group.add_option("--ignore-satisfy", action="store_true",
                         default=False,
                         help=_("Ignore unsatisfied dependency."))

        group.add_option("--ignore-safety", action="store_true",
                         default=False, help=_("Bypass safety switch."))
        group.add_option("-n", "--dry-run", action="store_true", default=False,
                         help=_("Do not perform any action, just show what would be done."))

    def init(self, database=True, write=True):
        super(PackageOp, self).init(database, write)


class InaryHelpFormatter(optparse.HelpFormatter):
    def __init__(self,
                 indent_increment=1,
                 max_help_position=32,
                 width=None,
                 short_first=1):
        optparse.HelpFormatter.__init__(
            self, indent_increment, max_help_position, width, short_first)

        self._short_opt_fmt = "{}"
        self._long_opt_fmt = "{}"

    def format_usage(self, usage):
        return _("usage: {}\n").format(usage)

    def format_heading(self, heading):
        return "%*s%s:\n" % (self.current_indent, "", heading)

    def format_option_strings(self, option):
        """Return a comma-separated list of option strings & metavariables."""
        if option.takes_value():
            short_opts = [self._short_opt_fmt.format(sopt)
                          for sopt in option._short_opts]
            long_opts = [self._long_opt_fmt.format(lopt)
                         for lopt in option._long_opts]
        else:
            short_opts = option._short_opts
            long_opts = option._long_opts

        if long_opts and short_opts:
            opt = "{0} [{1}]".format(short_opts[0], long_opts[0])
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
        else:  # start help on same line as opts
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
