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

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import os
import inary.util as util
import inary.context as ctx
import inary.cli
import inary.cli.command as command

class DeleteCache(command.Command, metaclass=command.autocommand):
    __doc__ = _("""Delete cache files

Usage: delete-cache

Sources, packages and temporary files are stored
under /var directory. Since these accumulate they can
consume a lot of disk space.""")

    def __init__(self, args=None):
        super(DeleteCache, self).__init__(args)

    name = ("delete-cache", "dc")

    def run(self):
        select = inary.cli.CLI().choose(str(_('Select cleaning directory:\n')) ,
                                              ['a) All cache','b) home-build cache (~/.inary)'])
        if select=='a) All cache':
            self.init(database=False, write=True)
            self.delete_cache()

        else:
            self.init()
            dest_dir = util.join_path(os.environ['HOME'], '.inary')
            ctx.ui.info(_("Cleaning home-build directory {}...").format(dest_dir))
            util.clean_dir(dest_dir)


    def delete_cache(self):
        """
        Deletes cached packages, cached archives, build dirs, db caches
        """
        ctx.ui.info(_("Cleaning package cache {}...").format(ctx.config.cached_packages_dir()))
        util.clean_dir(ctx.config.cached_packages_dir())
        ctx.ui.info(_("Cleaning source archive cache {}...").format(ctx.config.archives_dir()))
        util.clean_dir(ctx.config.archives_dir())
        ctx.ui.info(_("Cleaning temporary directory {}...").format(ctx.config.tmp_dir()))
        util.clean_dir(ctx.config.tmp_dir())
        for cache in [x for x in os.listdir(ctx.config.cache_root_dir()) if x.endswith(".cache")]:
            cache_file = util.join_path(ctx.config.cache_root_dir(), cache)
            ctx.ui.info(_("Removing cache file {}...").format(cache_file))
            os.unlink(cache_file)
