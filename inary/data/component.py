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


class Error(object, metaclass=autoxml.autoxml):
    pass


class Obsolete(metaclass=autoxml.autoxml):
    s_Package = [autoxml.String, autoxml.mandatory]

    def __str__(self):
        return self.package


class Distribution(xmlfile.XmlFile, metaclass=autoxml.autoxml):
    tag = "INARY"

    # name of distribution (source)
    t_SourceName = [autoxml.String, autoxml.mandatory]
    t_Description = [autoxml.LocalText, autoxml.mandatory]
    t_Version = [autoxml.String, autoxml.optional]
    t_Type = [autoxml.String, autoxml.mandatory]
    t_Dependencies = [[autoxml.Text],
                      autoxml.optional,
                      "Dependencies/Distribution"]

    # name of repository (binary distro)
    t_BinaryName = [autoxml.LocalText, autoxml.optional]
    # architecture identifier
    t_Architecture = [autoxml.Text, autoxml.optional]

    t_Obsoletes = [[Obsolete], autoxml.optional, "Obsoletes/Package"]


class Maintainer(xmlfile.XmlFile, metaclass=autoxml.autoxml):
    """representation for component responsibles"""

    t_Name = [autoxml.LocalText, autoxml.mandatory]
    t_Email = [autoxml.String, autoxml.mandatory]

    def __str__(self):
        s = "{0} <{1}>".format(self.name, self.email)
        return s


class Component(xmlfile.XmlFile, metaclass=autoxml.autoxml):
    """representation for component declarations"""

    t_Name = [autoxml.String, autoxml.mandatory]  # fully qualified name

    # component name in other languages, for instance in Turkish
    # LocalName for system.base could be sistem.taban or "Taban Sistem",
    # this could be useful for GUIs

    t_LocalName = [autoxml.LocalText, autoxml.optional]

    # Information about the component
    t_Summary = [autoxml.LocalText, autoxml.optional]
    t_Description = [autoxml.LocalText, autoxml.optional]
    t_Group = [autoxml.String, autoxml.optional]

    # Component responsible
    t_Maintainer = [Maintainer, autoxml.optional]

    # the parts of this component.
    # to be filled by the component database, thus it is optional.
    t_Packages = [[autoxml.String], autoxml.optional, "Parts/Package"]

    t_Sources = [[autoxml.String], autoxml.optional, "Parts/Source"]


class Components(xmlfile.XmlFile, metaclass=autoxml.autoxml):
    """representation for component declarations"""

    tag = "INARY"

    t_Components = [[Component], autoxml.optional, "Components/Component"]


# FIXME: there will be no component.xml only components.xml
class CompatComponent(Component):
    tag = "INARY"

    t_VisibleTo = [autoxml.String, autoxml.optional]
