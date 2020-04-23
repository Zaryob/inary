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
#
import os

import inary.context as ctx
import inary.util as util


class Trigger:
    def __init__(self):
        self.specdir=None
        self.Locals = None
        self.Globals = None
        self.postscript = None
        self.missing_postOps= False

    def load_script(self):
        """Compiles and executes the script"""
        compiled_script = self.compile_script()

        try:
            if not self.missing_postOps:
                localSymbols = globalSymbols = {}
                exec(compiled_script, localSymbols, globalSymbols)
            else:
                return 0
        except Exception as e:
            raise (e)

        self.Locals = localSymbols
        self.Globals = globalSymbols

    def compile_script(self):
        """Compiles the script and returns a code object"""

        fname = util.join_path(self.postscript)
        if os.path.isfile(fname):
            buf = open(fname).read()
            return compile(buf, fname, "exec")
        else:
            self.missing_postOps=True
            return None

    def run_command(self, func):
        """"""
        if not self.missing_postOps:
            curDir = os.getcwd()
            os.chdir(self.specdir)
            cmd_extra=""
            #FIXME: translate support needed
            if ctx.config.get_option('debug'):
                 ctx.ui.info(util.colorize("Running => {}",'brightgreen').format(util.colorize(func,"brightyellow")))
            else:    
                cmd_extra=" > /dev/null"
            ret_val=os.system('python3 -c \'import postoperations\nif(hasattr(postoperations,"{0}")):\n postoperations.{0}()\''.format(func)+cmd_extra)
            os.chdir(curDir)
            return (ret_val==0)
        else:
            return 0

    def preinstall(self, specdir):
        self.specdir=specdir
        self.postscript = util.join_path(self.specdir, ctx.const.postops)
        self.load_script()
        return self.run_command("preInstall")

    def postinstall(self, specdir):
        self.specdir=specdir
        self.postscript = util.join_path(self.specdir, ctx.const.postops)
        self.load_script()
        return self.run_command("postInstall")

    def postremove(self, specdir):
        self.specdir=specdir
        self.postscript = util.join_path(self.specdir, ctx.const.postops)
        self.load_script()
        return self.run_command("postRemove")

    def preremove(self, specdir):
        self.specdir=specdir
        self.postscript = util.join_path(self.specdir, ctx.const.postops)
        self.load_script()
        return self.run_command("preRemove")
