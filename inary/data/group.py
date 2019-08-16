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

import inary.sxml.autoxml as autoxml
import inary.sxml.xmlfile as xmlfile


class Group(xmlfile.XmlFile, metaclass=autoxml.autoxml):
    """representation for group declarations"""

    t_Name = [autoxml.String, autoxml.mandatory]
    t_LocalName = [autoxml.LocalText, autoxml.mandatory]
    t_Icon = [autoxml.String, autoxml.optional]


class Groups(xmlfile.XmlFile, metaclass=autoxml.autoxml):
    """representation for component declarations"""

    tag = "INARY"

    t_Groups = [[Group], autoxml.optional, "Groups/Group"]
