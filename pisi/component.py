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
# Author:  Eray Ozkural <eray@uludag.org.tr>

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.pxml.xmlfile as xmlfile
import pisi.pxml.autoxml as autoxml
import pisi.lockeddbshelve as shelve

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
    #t_Icon = [autoxml.Binary, autoxml.mandatory]
    
    # Dependencies to other components
    t_Dependencies = [ [autoxml.String], autoxml.optional, "Dependencies/Component"]

    # the parts of this component. 
    # to be filled by the component database, thus it is optional.
    t_Packages = [ [autoxml.String], autoxml.optional, "Parts/Package"]

    # TODO: this is probably not necessary since we use fully qualified 
    # module names (like in Java)
    #t_PartOf = [autoxml.Text, autoxml.mandatory]

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

class ComponentDB(object):
    """a database of components"""
    
    #FIXME: we might need a database per repo in the future
    def __init__(self):
        self.d = shelve.LockedDBShelf('components')

    def close(self):
        self.d.close()

    def has_component(self, name):
        return self.d.has_key(str(name))

    def get_component(self, name):
        if not self.has_component(name):
            self.d[name] = Component(name = name)
        return self.d[name]

    def list_components(self):
        list = []
        for (pkg, x) in self.d.iteritems():
            list.append(pkg)
        return list

    def update_component(self, component):
        if self.d.has_key(component.name):
            # preserve the list of packages
            component.packages = self.d[component.name].packages
        self.d[component.name] = component

    def add_package(self, component_name, package):
        component = self.get_component(component_name)
        component.packages.append(package)
        self.d[component_name] = component # update

    def remove_package(self, component_name, package):
        if not self.has_component(component_name):
            raise Error(_('Information for component %s not available') % component_name)
        component = self.get_component(component_name)
        component.packages.remove(package)
        self.d[component_name] = component # update

    def clear(self):
        self.d.clear()

    def remove_component(self, name):
        name = str(name)
        del self.d[name]
