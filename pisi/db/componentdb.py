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

import types

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx
import pisi.db.itembyrepodb as itembyrepodb
import pisi.component


class ComponentDB(object):

    def __init__(self):
        self.d = itembyrepodb.ItemByRepoDB('component')

    def close(self):
        self.d.close()

    def destroy(self):
        self.d.destroy()

    def has_component(self, name, repo = itembyrepodb.repos, txn = None):
        name = str(name)
        return self.d.has_key(name, repo, txn)

    def get_component(self, name, repo=None, txn = None):
        try:
            return self.d.get_item(name, repo, txn=txn)
        except itembyrepodb.NotfoundError, e:
            raise Error(_('Component %s not found') % name)

    def get_component_repo(self, name, repo=None, txn = None):
        try:
            return self.d.get_item_repo(name, repo, txn=txn)
        except itembyrepodb.NotfoundError, e:
            raise Error(_('Component %s not found') % name)

    def get_union_comp(self, name, txn = None, repo = itembyrepodb.repos ):
        """get a union of all repository components packages, not just the first repo in order.
        get only basic repo info from the first repo"""
        def proc(txn):
            s = self.d.d.get(name, txn=txn)
            pkgs = set()
            srcs = set()
            for repostr in self.d.order(repo = repo):
                if s.has_key(repostr):
                    pkgs |= set(s[repostr].packages)
                    srcs |= set(s[repostr].sources)
            comp = self.get_component(name)
            comp.packages = list(pkgs)
            comp.sources = list(srcs)
            return comp
        return self.d.txn_proc(proc, txn)

    def list_components(self, repo=None):
        return self.d.list(repo)

    # walk: walks through the underlying  components' packages
    def get_union_packages(self, component_name, walk=False, repo=pisi.db.itembyrepodb.repos, txn = None):
        """returns union of all repository component's packages, not just the first repo's 
        component's in order"""
        
        component = self.get_union_comp(component_name, txn, repo)
        if not walk:
            return component.packages

        packages = []
        packages.extend(component.packages)
        for dep in component.dependencies:
            packages.extend(self.get_union_packages(dep, walk, repo, txn))

        return packages

    # walk: walks through the underlying  components' packages
    def get_packages(self, component_name, walk=False, repo=None, txn = None):
        """returns the given component's and underlying recursive components' packages"""
        
        component = self.get_component(component_name, repo, txn)
        if not walk:
            return component.packages

        packages = []
        packages.extend(component.packages)
        for dep in component.dependencies:
            packages.extend(self.get_packages(dep, walk, repo, txn))

        return packages

    def add_child(self, component, repo, txn = None):
        """update component tree"""
        parent_name = ".".join(component.name.split(".")[:-1])
        if not parent_name: # root component
            return

        if self.has_component(parent_name, repo, txn):
            parent = self.get_component(parent_name, repo, txn)
        else:
            parent = pisi.component.Component(name = parent_name)

        if component.name not in parent.dependencies:
            parent.dependencies.append(component.name)
            self.d.add_item(parent_name, parent, repo, txn)

    def update_component(self, component, repo, txn = None):
        def proc(txn):
            if self.has_component(component.name, repo, txn):
                # preserve list of sources, packages and dependencies
                current = self.d.get_item(component.name, repo, txn)
                component.packages = current.packages
                component.sources = current.sources
                component.dependencies = current.dependencies
            self.d.add_item(component.name, component, repo, txn)
            self.add_child(component, repo, txn)
        self.d.txn_proc(proc, txn)

    def add_package(self, component_name, package, repo, txn = None):
        def proc(txn):
            assert component_name
            if self.has_component(component_name, repo, txn):
                component = self.get_component(component_name, repo, txn)
            else:
                component = pisi.component.Component( name = component_name )
            if not package in component.packages:
                component.packages.append(package)
            self.d.add_item(component_name, component, repo, txn) # update
            self.add_child(component, repo, txn)
        self.d.txn_proc(proc, txn)

    def remove_package(self, component_name, package, repo = None, txn = None):
        def proc(txn, repo):
            if not self.has_component(component_name, repo, txn):
                raise Error(_('Information for component %s not available') % component_name)
            if not repo:
                repo = self.d.which_repo(component_name, txn=txn) # get default repo then
            component = self.get_component(component_name, repo, txn)
            if package in component.packages:
                component.packages.remove(package)
            self.d.add_item(component_name, component, repo, txn) # update

        ctx.txn_proc(lambda x: proc(txn, repo), txn)

    def add_spec(self, component_name, spec, repo, txn = None):
        def proc(txn):
            assert component_name
            if self.has_component(component_name, repo, txn):
                component = self.get_component(component_name, repo, txn)
            else:
                component = pisi.component.Component( name = component_name )
            if not spec in component.sources:
                component.sources.append(spec)
            self.d.add_item(component_name, component, repo, txn) # update
            self.add_child(component, repo, txn)
        self.d.txn_proc(proc, txn)

    def remove_spec(self, component_name, spec, repo = None, txn = None):
        def proc(txn, repo):
            if not self.has_component(component_name, repo, txn):
                raise Error(_('Information for component %s not available') % component_name)
            if not repo:
                repo = self.d.which_repo(component_name, txn=txn) # get default repo then
            component = self.get_component(component_name, repo, txn)
            if spec in component.sources:
                component.sources.remove(spec)
            self.d.add_item(component_name, component, repo, txn) # update

        ctx.txn_proc(lambda x: proc(txn, repo), txn)

    def clear(self, txn = None):
        self.d.clear(txn)

    def remove_component(self, name, repo = None, txn = None):
        name = str(name)
        self.d.remove_item(name, repo, txn)

    def remove_repo(self, repo, txn = None):
        self.d.remove_repo(repo, txn=txn)
