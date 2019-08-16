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

import re
import sys
import tty
import locale


import inary.ui
import inary.errors
import inary.context as ctx
import inary.util as util

import gettext

__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class Error(inary.errors.Error):
    pass


class Exception(inary.errors.Exception):
    pass


# in old releases used this printu function
def printu(obj, err=False):
    if not isinstance(obj, str):
        obj = str(obj)
    if err:
        out = sys.stderr
    else:
        out = sys.stdout
    out.write(str(obj))
    out.flush()


class CLI(inary.ui.UI):
    """Command Line Interface"""

    def __init__(self, show_debug=False, show_verbose=False):
        super(CLI, self).__init__(show_debug, show_verbose)
        self.warnings = 0
        self.errors = 0

    def close(self):
        util.xterm_title_reset()

    def output(self, msg, err=False, verbose=False):
        if (verbose and self.show_verbose) or (not verbose):
            if isinstance(msg, bytes):
                msg = msg.decode('utf-8')
            if err:
                sys.stderr.write(str(msg))
            else:
                sys.stdout.write(str(msg))

    def formatted_output(self, msg, verbose=False, noln=False, column=":"):
        key_width = 20
        line_format = "%(key)-20s%(column)s%(rest)s"
        term_height, term_width = util.get_terminal_size()

        def find_whitespace(s, i):
            while s[i] not in (" ", "\t"):
                i -= 1
            return i

        def align(s):
            align_width = term_width - key_width - 2
            s_width = len(s)
            new_s = ""
            index = 0
            while True:
                next_index = index + align_width
                if next_index >= s_width:
                    new_s += s[index:]
                    break
                next_index = find_whitespace(s, next_index)
                new_s += s[index:next_index]
                index = next_index
                if index < s_width:
                    new_s += "\n" + " " * (key_width + 1)
            return new_s

        new_msg = ""
        for line in msg.split("\n"):
            key, _column, rest = line.partition(column)
            rest = align(rest)
            new_msg += line_format % {"key": key,
                                      "column": _column,
                                      "rest": rest}
            if not noln:
                new_msg = "{}\n".format(new_msg)
        msg = new_msg
        self.output(str(msg), verbose=verbose)

    def info(self, msg, verbose=False, noln=False, color='default'):
        # TODO: need to look at more kinds of info messages
        # let's cheat from KDE :)
        msg = util.colorize(msg, color)
        if verbose:
            msg = util.colorize(_('Verboses: '), 'brightwhite') + msg
        if not noln:
            msg = '{}\n'.format(msg)

        self.output(str(msg), verbose=verbose)

    def warning(self, msg, verbose=False):
        msg = str(msg)
        self.warnings += 1
        if ctx.log:
            ctx.log.warning(msg)
        if ctx.get_option('no_color'):
            self.output(_('Warning: ') + msg + '\n', err=True, verbose=verbose)
        else:
            self.output(util.colorize(msg + '\n', 'brightyellow'), err=True, verbose=verbose)

    def error(self, msg):
        msg = str(msg)
        self.errors += 1
        if ctx.log:
            ctx.log.error(msg)
        if ctx.get_option('no_color'):
            self.output(_('Error: ') + msg + '\n', err=True)
        else:
            self.output(util.colorize(msg + '\n', 'brightred'), err=True)

    def action(self, msg, verbose=False):
        # TODO: this seems quite redundant?
        msg = str(msg)
        if ctx.log:
            ctx.log.info(msg)
        self.output(util.colorize(msg + '\n', 'green'))

    def choose(self, msg, opts):
        msg = str(msg)
        endmsg = '\n Select one:'
        prompt = msg + util.colorize('[  %s  ]' % ("  /   ".join(opts)), 'brightblue') + endmsg

        while True:
            s = input(prompt)
            for opt in opts:
                if opt.startswith(str(s)):
                    return opt

    def confirm(self, msg):
        msg = str(msg)
        if ctx.config.options and ctx.config.options.yes_all:
            return True

        locale.setlocale(locale.LC_ALL, "")
        yes_expr = re.compile(locale.nl_langinfo(locale.YESEXPR))
        no_expr = re.compile(locale.nl_langinfo(locale.NOEXPR))
        locale.setlocale(locale.LC_ALL, "C")

        while True:
            tty.tcflush(sys.stdin.fileno(), 0)
            prompt = msg + util.colorize(" "+_('(yes'), 'green') + '/' + util.colorize(_('no)'), 'red') + ":  "
            s = input(prompt)

            if yes_expr.search(s):
                return True

            if no_expr.search(s):
                return False

    def display_progress(self, **ka):
        """ display progress of any operation """
        if ka['operation'] in ["removing", "rebuilding-db"]:
            return

        elif ka['operation'] == "fetching":
            totalsize = '%.1f %s' % util.human_readable_size(ka['total_size'])

            out = '\r%-30.50s  (%s) %3d%% %9.2f %s [%s]' % \
                  (ka['filename'], totalsize, ka['percent'],
                   ka['rate'], ka['symbol'], ka['eta'])
            self.output(out)
        else:
            self.output("\r%s (%d%%)" % (ka['info'], ka['percent']))

    def status(self, msg=None, push_screen=True):
        if msg:
            msg = str(msg)
            if push_screen:
                self.output(util.colorize(msg + '\n', 'brightgreen'))
            util.xterm_title(msg)

    def notify(self, event, logging=True, **keywords):
        if event == inary.ui.installed:
            msg = _('Installed \"{}\"').format(keywords['package'].name)
            color = 'brightgreen'
        elif event == inary.ui.installing:
            msg = _('Installing \"{0.name}\", version {0.version}, release {0.release}').format(keywords['package'])
            color = 'brightblue'
        elif event == inary.ui.removed:
            msg = _('Removed \"{}\"').format(keywords['package'].name)
            color = 'brightgreen'
        elif event == inary.ui.removing:
            msg = _('Removing \"{}\"').format(keywords['package'].name)
            color = 'brightpurple'
        elif event == inary.ui.upgraded:
            msg = _('Upgraded \"{}\"').format(keywords['package'].name)
            color = 'brightgreen'
        elif event == inary.ui.configured:
            msg = _('Configured \"{}\"').format(keywords['package'].name)
            color = 'brightgreen'
        elif event == inary.ui.configuring:
            msg = _('Configuring \"{}\"').format(keywords['package'].name)
            color = 'faintyellow'
        elif event == inary.ui.extracting:
            msg = _('Extracting the files of \"{}\"').format(keywords['package'].name)
            color = 'faintgreen'
        elif event == inary.ui.updatingrepo:
            msg = _('Updating package repository: \"{}\"').format(keywords['name'])
            color = 'green'
        elif event == inary.ui.cached:
            total_size, total_symbol = util.human_readable_size(keywords['total'])
            cached_size, cached_symbol = util.human_readable_size(keywords['cached'])
            msg = _('Total size of package(s): {:.2f} {} / {:.2f} {}').format(cached_size,
                                                                              cached_symbol,
                                                                              total_size,
                                                                              total_symbol)
            color = 'cyan'
        elif event == inary.ui.packagestogo:
            if ctx.log:
                ctx.log.info(_("Following packages ordered for process: {}").format(keywords['order']))
            msg = None

        elif event == inary.ui.desktopfile:
            if ctx.log:
                ctx.log.info(_("Extracted desktop file \"{}\"").format(keywords['desktopfile']))
            msg = None

        else:
            msg = None

        if msg:
            self.output(util.colorize(msg + '\n', color))
            if ctx.log and logging:
                ctx.log.info(msg)
