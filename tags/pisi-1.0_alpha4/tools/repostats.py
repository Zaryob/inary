#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#

import sys
import os

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

sys.path.append('.')
import pisi.specfile
import pisi.uri

def echo(string):
    print string.encode("utf8")

def valuesort(x, y):
    if x[1] > y[1]:
        return -1
    elif x[1] == y[1]:
        return 0
    else:
        return 1


class Histogram:
    def __init__(self, title):
        self.list = {}
        self.title = title
    
    def add(self, name, value=None):
        if value:
            self.list[name] = value
        else:
            if self.list.has_key(name):
                self.list[name] = self.list[name] + 1
            else:
                self.list[name] = 1
    
    def get_list(self):
        items = self.list.items()
        items.sort(valuesort)
        return items
    
    def html_out(self, max=0):
        echo("<h1>%s</h1><table>" % self.title)
        list = self.get_list()
        if max != 0:
            list = list[:max]
        for name,cnt in list:
            echo("<tr><td>%s</td><td>%s</td></tr>" % (name, cnt))
        echo("</table>")


def scan_pspec(folder):
    paks = []
    for root, dirs, files in os.walk(folder):
        if "pspec.xml" in files:
            paks.append(root)
        # dont walk into the versioned stuff
        if ".svn" in dirs:
            dirs.remove(".svn")
    return paks

def add_deps(deps, spec):
    a = {}
    for d in spec.source.buildDeps:
        p = d.package
        if not a.has_key(p):
            a[p] = 1
    for pak in spec.packages:
        for d in pak.runtimeDeps:
            p = d.package
            if not a.has_key(p):
                a[p] = 1
    for p in a:
        deps.add(p)

hosts = Histogram(_("Source hosts"))
people = Histogram(_("Packagers"))
licenses = Histogram(_("Licenses"))
categories = Histogram(_("Categories"))
components = Histogram(_("Components"))
dependencies = Histogram(_("Dependencies"))
releases = Histogram(_("Releases"))
types = Histogram(_("File types"))
mostpatched = Histogram(_("Top five most patched source"))
longpy = Histogram(_("Top five longest action.py scripts"))
nr_binpaks = 0
nr_patches = 0
paknames = {}

errors = []

paks = scan_pspec(sys.argv[1])
for pak in paks:
    spec = pisi.specfile.SpecFile()
    try:
        spec.read(os.path.join(pak, "pspec.xml"))
    except Exception, inst:
        errors.append([pak, str(inst)])
        continue
    try:
        f = file(os.path.join(pak, "actions.py"))
        L = len(f.readlines())
        longpy.add(spec.source.name, L)
        f.close()
    except:
        pass
    nr_binpaks += len(spec.packages)
    nr_patches += len(spec.source.patches)
    mostpatched.add(spec.source.name, len(spec.source.patches))
    releases.add(str(spec.source.release))
    for p in spec.packages:
        if p.partof:
            components.add(p.partof)
        for x in p.isa:
            categories.add(x)
        for x in p.paths:
            types.add(x.fileType)
    paknames[spec.source.name] = 1
    add_deps(dependencies, spec)
    name = spec.source.packager.name
    lices = spec.source.license
    people.add(name)
    for lice in lices:
        licenses.add(lice)
    host = pisi.uri.URI(spec.source.archiveUri).location()
    if host == "":
        print pisi.uri.URI(spec.source.archiveUri)
    hosts.add(host)

print "<html><head><title>%s İstatistikleri</title>" % (sys.argv[1])
print '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
echo("</head><body>")

print "<p>Toplam %d kod paketi, ve bunlardan oluşturulacak %d ikili paket var.</p>" % (len(paks), nr_binpaks)
echo(u"<p>Toplam peç sayısı %d</p>" % nr_patches)

mostpatched.html_out(5)
longpy.html_out(5)

if errors != []:
    print "<h1>Hatalar</h1><table>"
    for e in errors:
        print "<tr><td>%s</td><td>%s</td></tr>" % (e[0], e[1])
    print "</table>"
else:
    print "<p>Hata yok, tebrikler!</p>"

components.html_out()
categories.html_out()
people.html_out()
licenses.html_out()
releases.html_out()
types.html_out()

echo(_("<h1>Dependencies<br>"))
echo(_("<small>package name with italics are not available in the repository</small></h1>"))
print "<table>"
notavail = 0
for name,cnt in dependencies.get_list():
    if paknames.has_key(name):
        print "<tr><td><b>%s</b></td><td>%d</td></tr>" % (name, cnt)
    else:
        notavail += 1
        print "<tr><td><i>%s</i></td><td>%d</td></tr>" % (name, cnt)
print "</table>"

print "<p>%d packages are not available in repository.</p>" % notavail

hosts.html_out()

print "</body>"
