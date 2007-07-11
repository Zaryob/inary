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

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx
import pisi.pxml.xmlfile as xmlfile
import pisi.pxml.autoxml as autoxml
import pisi.db.lockeddbshelve as shelve
import pisi.db.itembyrepodb

class Error(pisi.Error):
    pass

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

class Component(xmlfile.XmlFile):
    "representation for component declarations"

    __metaclass__ = autoxml.autoxml

    tag = "PISI"

    t_Name = [autoxml.String, autoxml.mandatory]     # fully qualified name

    # component name in other languages, for instance in Turkish
    # LocalName for system.base could be sistem.taban or "Taban Sistem",
    # this could be useful for GUIs

    t_LocalName = [autoxml.LocalText, autoxml.mandatory]

    # Information about the component
    t_Summary = [autoxml.LocalText, autoxml.mandatory]
    t_Description = [autoxml.LocalText, autoxml.mandatory]
    t_Icon = [ autoxml.String, autoxml.optional]
    t_VisibleTo = [autoxml.String, autoxml.optional]

    # Dependencies to other components
    t_Dependencies = [ [autoxml.String], autoxml.optional, "Dependencies/Component"]

    # the parts of this component.
    # to be filled by the component database, thus it is optional.
    t_Packages = [ [autoxml.String], autoxml.optional, "Parts/Package"]

    t_Sources = [ [autoxml.String], autoxml.optional, "Parts/Source"]
