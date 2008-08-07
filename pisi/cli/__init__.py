# -*- coding: utf-8 -*-
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

import sys
import logging
import locale

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx
import pisi.ui
import pisi.util

class Error(pisi.Error):
    pass


class Exception(pisi.Exception):
    pass


def printu(obj, err = False):
    if not isinstance(obj, unicode):
        obj = unicode(obj)
    if err:
        out = sys.stderr
    else:
        out = sys.stdout
    out.write(obj.encode('utf-8'))
    out.flush()

class CLI(pisi.ui.UI):
    "Command Line Interface"

    def __init__(self, show_debug = False, show_verbose = False):
        super(CLI, self).__init__(show_debug, show_verbose)

    def close(self):
        pisi.util.xterm_title_reset()

    def output(self, msg, err = False, verbose = False):
        if (verbose and self.show_verbose) or (not verbose):
            if type(msg)==type(unicode()):
                msg = msg.encode('utf-8')
            if err:
                out = sys.stderr
            else:
                out = sys.stdout
            out.write(msg)
            out.flush()

    def info(self, msg, verbose = False, noln = False):
        # TODO: need to look at more kinds of info messages
        # let's cheat from KDE :)
        if not noln:
            msg = '%s\n' % msg
        self.output(unicode(msg), verbose=verbose)

    def warning(self, msg, verbose = False):
        msg = unicode(msg)
        if ctx.log:
            ctx.log.warning(msg)
        if ctx.get_option('no_color'):
            self.output(_('Warning: ') + msg + '\n', err=True, verbose=verbose)
        else:
            self.output(pisi.util.colorize(msg + '\n', 'brightred'), err=True, verbose=verbose)

    def error(self, msg):
        msg = unicode(msg)
        if ctx.log:
            ctx.log.error(msg)
        if ctx.get_option('no_color'):
            self.output(_('Error: ') + msg + '\n', err=True)
        else:
            self.output(pisi.util.colorize(msg + '\n', 'red'), err=True)

    def action(self, msg, verbose = False):
        #TODO: this seems quite redundant?
        msg = unicode(msg)
        if ctx.log:
            ctx.log.info(msg)
        self.output(pisi.util.colorize(msg + '\n', 'green'))

    def choose(self, msg, opts):
        print msg
        for i in range(0,len(opts)):
            print i + 1, opts(i)
        while True:
            s = raw_input(msg + pisi.util.colorize('1-%d' % len(opts), 'red'))
            try:
                opt = int(s)
                if 1 <= opt and opt <= len(opts):
                    return opts(opt-1)
            except Exception:
                pass

    def confirm(self, msg):
        msg = unicode(msg)
        if ctx.config.options and ctx.config.options.yes_all:
            return True
        while True:
            import re
            yesexpr = re.compile(locale.nl_langinfo(locale.YESEXPR))

            prompt = msg + pisi.util.colorize(_(' (yes/no)'), 'red')
            s = raw_input(prompt.encode('utf-8'))
            if yesexpr.search(s):
                return True

            return False

    def display_progress(self, **ka):
        """ display progress of any operation """
        if ka['operation'] in ["removing", "rebuilding-db"]:
            return
        elif ka['operation'] == "fetching":
            totalsize = '%.1f %s' % pisi.util.human_readable_size(ka['total_size'])
            out = '\r%-30.50s (%s)%3d%% %9.2f %s [%s]' % \
                (ka['filename'], totalsize, ka['percent'],
                 ka['rate'], ka['symbol'], ka['eta'])
            self.output(out)
        else:
            self.output("\r%s (%d%%)" % (ka['info'], ka['percent']))

        if ka['percent'] == 100:
            self.output(pisi.util.colorize(_(' [complete]\n'), 'gray'))

    def status(self, msg = None):
        if msg:
            msg = unicode(msg)
            self.output(pisi.util.colorize(msg + '\n', 'brightgreen'))
            pisi.util.xterm_title(msg)

    def notify(self, event, **keywords):
        if event == pisi.ui.installed:
            msg = _('Installed %s') % keywords['package'].name
        elif event == pisi.ui.removed:
            msg = _('Removed %s') % keywords['package'].name
        elif event == pisi.ui.upgraded:
            msg = _('Upgraded %s') % keywords['package'].name
        elif event == pisi.ui.configured:
            msg = _('Configured %s') % keywords['package'].name
        elif event == pisi.ui.extracting:
            msg = _('Extracting the files of %s') % keywords['package'].name
        else:
            msg = None
        if msg:
            self.output(pisi.util.colorize(msg + '\n', 'cyan'))
            if ctx.log:
                ctx.log.info(msg)
