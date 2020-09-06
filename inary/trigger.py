# -*- coding:utf-8 -*-
#
# Copyright (C) 2020, Sulin Community
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
# Developed by:
#   Ali Rıza Keskin (sulincix)
#   Suleyman Poyraz (Zaryob)

# Standard Python Modules
import os

# INARY Modules
import inary.context as ctx
import inary.util as util


class Trigger:
    def __init__(self):
        self.specdir = None
        self.Locals = None
        self.Globals = None
        self.postscript = None
        self.missing_postOps = False

    def run_command(self, func):
        """Run postOps scripts"""
        if os.path.exists(self.specdir+"/"+ctx.const.postops[1]):
            curDir = os.getcwd()
            os.chdir(self.specdir)
            cmd_extra = ""
            # FIXME: translate support needed
            if ctx.config.get_option('debug'):
                ctx.ui.info(
                    util.colorize(
                        "Running => {}",
                        'brightgreen').format(
                        util.colorize(
                            func,
                            "brightyellow")))
            else:
                cmd_extra = " > /dev/null"
            ret_val = os.system(
                'bash --noprofile --norc -c \'source postoperations.sh ; if declare -F {0} &>/dev/null ; then {0} ; fi\''.format(func) +
                cmd_extra)
            os.chdir(curDir)
            if (ret_val != 0):
                return False
        if os.path.exists(self.specdir+"/"+ctx.const.postops[0]):
            curDir = os.getcwd()
            os.chdir(self.specdir)
            cmd_extra = ""
            # FIXME: translate support needed
            if ctx.config.get_option('debug'):
                ctx.ui.info(
                    util.colorize(
                        "Running => {}",
                        'brightgreen').format(
                        util.colorize(
                            func,
                            "brightyellow")))
            else:
                cmd_extra = " > /dev/null"
            ret_val = os.system(
                'python3 -c \'import postoperations\nif(hasattr(postoperations,"{0}")):\n postoperations.{0}()\''.format(func) +
                cmd_extra)
            os.chdir(curDir)
            if (ret_val != 0):
                return False
        return True

    def preinstall(self, specdir):
        self.specdir = specdir
        for postops in ctx.const.postops:
            self.postscript = util.join_path(self.specdir, postops)
            retval = self.run_command("preInstall")
            util.delete_file(self.postscript)
        return retval

    def postinstall(self, specdir):
        self.specdir = specdir
        for postops in ctx.const.postops:
            self.postscript = util.join_path(self.specdir, postops)
        return self.run_command("postInstall")

    def postremove(self, specdir):
        self.specdir = specdir
        for postops in ctx.const.postops:
            self.postscript = util.join_path(self.specdir, postops)
        return self.run_command("postRemove")

    def preremove(self, specdir):
        self.specdir = specdir
        for postops in ctx.const.postops:
            self.postscript = util.join_path(self.specdir, postops)
        return self.run_command("preRemove")
