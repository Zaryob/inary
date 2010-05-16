# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 - 2007, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import pisi.pxml.xmlfile as xmlfile
import pisi.pxml.autoxml as autoxml

class Error(object):

    __metaclass__ = autoxml.autoxml

class Obsolete:

    __metaclass__ = autoxml.autoxml

    s_Package = [autoxml.String, autoxml.mandatory]

    def __str__(self):
        return self.package

class Distribution(xmlfile.XmlFile):

    __metaclass__ = autoxml.autoxml

    tag = "PISI"

    t_SourceName = [autoxml.Text, autoxml.mandatory] # name of distribution (source)
    t_Description = [autoxml.LocalText, autoxml.mandatory]
    t_Version = [autoxml.Text, autoxml.optional]
    t_Type =  [autoxml.Text, autoxml.mandatory]
    t_Dependencies = [ [autoxml.Text], autoxml.optional, "Dependencies/Distribution"]

    t_BinaryName = [autoxml.Text, autoxml.optional] # name of repository (binary distro)
    t_Architecture = [autoxml.Text, autoxml.optional] # architecture identifier

    t_Obsoletes = [ [Obsolete], autoxml.optional, "Obsoletes/Package"]

class Maintainer(xmlfile.XmlFile):
    "representation for component responsibles"

    __metaclass__ = autoxml.autoxml

    t_Name = [autoxml.Text, autoxml.mandatory]
    t_Email = [autoxml.String, autoxml.mandatory]

    def __str__(self):
        s = "%s <%s>" % (self.name, self.email)
        return s

class Component(xmlfile.XmlFile):
    "representation for component declarations"

    __metaclass__ = autoxml.autoxml

    t_Name = [autoxml.String, autoxml.mandatory]     # fully qualified name

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
    t_Packages = [ [autoxml.String], autoxml.optional, "Parts/Package"]

    t_Sources = [ [autoxml.String], autoxml.optional, "Parts/Source"]

class Components(xmlfile.XmlFile):
    "representation for component declarations"

    __metaclass__ = autoxml.autoxml

    tag = "PISI"

    t_Components = [ [Component], autoxml.optional, "Components/Component" ]

# FIXME: there will be no component.xml only components.xml
class CompatComponent(Component):

    tag = "PISI"

    t_VisibleTo = [autoxml.String, autoxml.optional]
