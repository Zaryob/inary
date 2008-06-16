# -*- coding:utf-8 -*-
#
# Copyright (C) 2005 - 2008, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import optparse

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.api
import pisi.cli.command as command
import pisi.context as ctx

class AddRepo(command.Command):
    """Add a repository

Usage: add-repo <repo> <indexuri>

<repo>: name of repository to add
<indexuri>: URI of index file

If no repo is given, add-repo pardus-devel repo is added by default

NB: We support only local files (e.g., /a/b/c) and http:// URIs at the moment
"""
    __metaclass__ = command.autocommand

    def __init__(self, args):
        super(AddRepo, self).__init__(args)

    name = ("add-repo", "ar")

    def options(self):

        group = optparse.OptionGroup(self.parser, _("add-repo options"))
        group.add_option("--at", action="store",
                               type="int", default=None,
                               help=_("Add repository at given position (0 is first)"))
        self.parser.add_option_group(group)

    def run(self):

        if len(self.args)==2 or len(self.args)==0:
            self.init()
            if len(self.args)==2:
                name = self.args[0]
                indexuri = self.args[1]
            else:
                name = 'pardus-2008'
                indexuri = 'http://paketler.pardus.org.tr/pardus-2008/pisi-index.xml.bz2'
            pisi.api.add_repo(name, indexuri, ctx.get_option('at'))
            if ctx.ui.confirm(_('Update PiSi database for repository %s?') % name):
                try:
                    pisi.api.update_repo(name)
                except pisi.fetcher.FetchError:
                    ctx.ui.warning(_("%s repository could not be reached. Removing %s from system.") % (name, name))
                    pisi.api.remove_repo(name)
        else:
            self.help()
            return
