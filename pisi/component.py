# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
# Authors:  Eray Ozkural <eray@uludag.org.tr>

"""a placeholder for data types, might factor elsewhere later"""

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.pxml.xmlfile as xmlfile
import pisi.pxml.autoxml as autoxml

class Error(pisi.Error):
    pass

__metaclass__ = autoxml.autoxml


class Distribution:
    t_Name = [autoxml.Text, autoxml.mandatory]
    t_Description = [autoxml.LocalText, autoxml.mandatory]
    t_Version = [autoxml.Text, autoxml.mandatory]
    t_Type =  [autoxml.Text, autoxml.mandatory]
    t_Dependencies = [ [autoxml.Text], autoxml.optional, "Dependencies/Distribution"]


class Component(xmlfile.XmlFile):
    "part-of representation for component declarations"

    __metaclass__ = autoxml.autoxml

    tag = "PISI"
    
    t_Name = [autoxml.Text, autoxml.mandatory]     # fully qualified name
    t_PartOf = [autoxml.Text, autoxml.mandatory]
    t_LocalName = [autoxml.LocalText, autoxml.mandatory]
    t_Description = [autoxml.LocalText, autoxml.mandatory]
    #t_Icon = [autoxml.Binary, autoxml.mandatory]
    t_Dependencies = [ [autoxml.String], autoxml.optional, "Dependencies/Component"]


#FIXME: recursive declarations do not work!
#class ComponentTree(xmlfile.XmlFile):
#    "index representation for the component structure"
#
#    __metaclass__ = autoxml.autoxml
#
#    tag = "Component"
#    
#    t_Name = [autoxml.Text, autoxml.mandatory]    # fully qualified name
#    #t_Icon = [autoxml.Binary, autoxml.mandatory]
#    t_Dependencies = [ [autoxml.Text], autoxml.optional, "Component"]
#    #t_Parts = [ [pisi.component.ComponentTree], autoxml.optional, "Component"]

