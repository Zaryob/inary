# -*- coding:utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import optparse
import os
import sys

import gettext

__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

from inary.operations import history
import inary.db
import inary.context as ctx
import inary.util as util
import inary.cli.command as command

# Operation names for translation
opttrans = {"upgrade": _("upgrade"), "remove": _("remove"), "emerge": _("emerge"), "install": _("install"),
            "snapshot": _("snapshot"), "takeback": _("takeback"), "repoupdate": _("repository update")}


class History(command.PackageOp, metaclass=command.autocommand):
    __doc__ = _("""History of inary operations

Usage: history

Lists previous operations.""")

    def __init__(self, args=None):
        super(History, self).__init__(args)
        self.historydb = inary.db.historydb.HistoryDB()

    name = ("history", "hs")

    def options(self):

        group = optparse.OptionGroup(self.parser, _("history options"))

        group.add_option("-l", "--last", action="store", type="int", default=0,
                         help=_("Output only the last \'n\' operations."))
        group.add_option("-s", "--snapshot", action="store_true", default=False,
                         help=_("Take snapshot of the current system."))
        group.add_option("-t", "--takeback", action="store", type="int", default=-1,
                         help=_("Takeback to the state after the given operation finished."))

        self.parser.add_option_group(group)

    @staticmethod
    def take_snapshot():
        history.snapshot()

    @staticmethod
    def takeback(operation):
        history.takeback(operation)

    def print_history(self):
        ordered_history = []
        ordered_history.append(_("Inary Transaction History: "))
        for operation in self.historydb.get_last(ctx.get_option('last')):

            msg_oprt = util.colorize(_("Operation "),'none','yellow') \
                       + util.colorize("#{}: ".format(operation.no),'none', "blue") \
                       + util.colorize("{}:".format(opttrans[operation.type]),'none', "white")

            date_and_time = util.colorize(_("Date: "),'none', "cyan") + "{0.date} {0.time}".format(operation)
            ordered_history.append(msg_oprt)
            ordered_history.append(date_and_time)

            if operation.type == "snapshot":
                msg_snap = util.colorize(
                    _("    * There are {} packages in this snapshot.").format(len(operation.packages)),
                    'none',"purple")

                ordered_history.append(msg_snap)
            elif operation.type == "repoupdate":
                for repo in operation.repos:
                    ordered_history.append("    * " + repo.name)
            else:
                for pkg in operation.packages:
                    ordered_history.append("    * " + pkg.name)
        return ordered_history

    def redirect_output(self, order):
    #    if os.isatty(sys.stdout.fileno()):
        class LessException(Exception):
            pass

        class LessPipe():
            def __init__(self):
                import subprocess
                self.less = subprocess.Popen(["less", "-K", "-R", "-"],
                                             stdin=subprocess.PIPE)

            def close(self):
                self.less.stdin.close()
                self.less.wait()
                self.less.kill()

            def flush(self):
                self.less.stdin.flush()

            def write(self, s):
                try:
                    self.less.stdin.write(bytes(s.encode("utf-8")))
                except IOError:
                    raise LessException

        pipe=LessPipe()

        try:
            for i in order:
                pipe.write(i)
                pipe.write("\n")
            pipe.close()
        except LessException:
            pass

    def run(self):
        self.init(database=False, write=False)
        if ctx.get_option('snapshot'):
            self.take_snapshot()
            return
        elif ctx.get_option('takeback'):
            opno = ctx.get_option('takeback')
            if opno != -1:
                self.takeback(opno)
                return

        self.redirect_output(self.print_history())
