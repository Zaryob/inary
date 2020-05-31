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

# Inary Modules
import inary.db
import inary.context as ctx


def search_package(terms, lang=None, repo=None):
    """
    Return a list of packages that contains all the given terms either in its name, summary or
    description -> list_of_strings
    @param terms: a list of terms used to search package -> list_of_strings
    @param lang: language of the summary and description
    @param repo: Repository of the packages. If repo is None than returns a list of all the packages
    in all the repositories that meets the search
    """
    packagedb = inary.db.packagedb.PackageDB()
    return packagedb.search_package(terms, lang, repo)


def search_installed(terms, lang=None):
    """
    Return a list of components that contains all the given terms either in its name, summary or
    description -> list_of_strings
    @param terms: a list of terms used to search components -> list_of_strings
    @param lang: language of the summary and description
    """
    installdb = inary.db.installdb.InstallDB()
    return installdb.search_package(terms, lang)


def search_source(terms, lang=None, repo=None):
    """
    Return a list of source packages that contains all the given terms either in its name, summary or
    description -> list_of_strings
    @param terms: a list of terms used to search source package -> list_of_strings
    @param lang: language of the summary and description
    @param repo: Repository of the source packages. If repo is None than returns a list of all the source
    packages in all the repositories that meets the search
    """
    sourcedb = inary.db.sourcedb.SourceDB()
    return sourcedb.search_spec(terms, lang, repo)


def search_component(terms, lang=None, repo=None):
    """
    Return a list of components that contains all the given terms either in its name, summary or
    description -> list_of_strings
    @param terms: a list of terms used to search components -> list_of_strings
    @param lang: language of the summary and description
    @param repo: Repository of the components. If repo is None than returns a list of all the components
    in all the repositories that meets the search
    """
    componentdb = inary.db.componentdb.ComponentDB()
    return componentdb.search_component(terms, lang, repo)


def search_file(term):
    """
    Returns a tuple of package and matched files list that matches the files of the installed
    packages -> list_of_tuples
    @param term: used to search file -> list_of_strings

    >>> import inary.operations
    >>> files = inary.operations.search.search_file("kvm-")

    >>> print files

    >>> [("kvm", (["lib/modules/2.6.18.8-86/extra/kvm-amd.ko","lib/modules/2.6.18.8-86/extra/kvm-intel.ko"])),]
    """
    if term.startswith("/"):
        term = term[1:]
    return ctx.filesdb.search_file(term)
