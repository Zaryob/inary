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

import os.path

import inary.context as ctx
import inary.errors

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


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
            raise inary.errors.Error(_('Mirrors file \"{}\" does not exist. Could not resolve \"mirrors://\"').format(config))
