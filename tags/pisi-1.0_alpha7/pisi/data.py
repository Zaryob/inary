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

import pisi.xmlfile

__metaclass__ = xmlfile.autoxml

class Distribution:
    t_Name = [xmlfile.Text, xmlfile.mandatory]
    t_Description = [xmlfile.LocalText, xmlfile.mandatory]
    t_Version = [xmlfile.Text, xmlfile.mandatory]
    t_Type =  [xmlfile.Text, xmlfile.mandatory]
    t_Dependencies = [ [xmlfile.Text], xmlfile.optional, "Distribution"]

class Component:
    "part-of representation for component declarations"
    
    t_Name = [xmlfile.Text, xmlfile.mandatory]     # fully qualified name
    t_PartOf = [xmlfile.Text, xmlfile.mandatory]
    t_LocalName = [xmlfile.LocalText, xmlfile.mandatory]
    t_Description = [xmlfile.LocalText, xmlfile.mandatory]
    #t_Icon = [xmlfile.Binary, xmlfile.mandatory]
    t_Dependencies = [ [xmlfile.String], xmlfile.optional, "Component"]

class ComponentTree:
    "index representation for the component structure"
    tag = "Component"
    
    t_Name = [xmlfile.Text, xmlfile.mandatory]    # fully qualified name
    #t_Icon = [xmlfile.Binary, xmlfile.mandatory]
    t_Dependencies = [ [xmlfile.Text], xmlfile.optional, "Component"]
    t_Parts = [ [ComponentTree], xmlfile.optional, "Component"]
