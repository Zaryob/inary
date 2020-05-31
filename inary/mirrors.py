# -*- coding: utf-8 -*-
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

# Standard Python Modules
import os.path

# INARY Modules
import inary.context as ctx
import inary.errors

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class MirrorError(inary.errors.Error):
    pass


class Mirrors:
    def __init__(self, config=ctx.const.mirrors_conf):
        self.mirrors = {}
        self._parse(config)

    def get_mirrors(self, name):
        if name in self.mirrors:
            return list(self.mirrors[name])

        return None

    def _add_mirror(self, name, url):
        if name in self.mirrors:
            self.mirrors[name].append(url)
        else:
            self.mirrors[name] = [url]

    def _parse(self, config):
        if os.path.exists(config):
            for line in open(config).readlines():
                if not line.startswith('#') and not line == '\n':
                    mirror = line.strip().split()
                    if len(mirror) == 2:
                        (name, url) = mirror
                        self._add_mirror(name, url)
        else:
            raise inary.errors.Error(
                _('Mirrors file \"{}\" does not exist. Could not resolve \"mirrors://\"').format(config))
