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
#

# AutoXML Library
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
