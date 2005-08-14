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

sys.path.append('.')
import pisi.specfile
import pisi.uri

class Histogram:
    def __init__(self):
        self.list = {}
    
    def add(self, name):
        if self.list.has_key(name):
            self.list[name] = self.list[name] + 1
        else:
            self.list[name] = 1
    
    def _sortfunc(self, x, y):
        if x[1] > y[1]:
            return -1
        elif x[1] == y[1]:
            return 0
        else:
            return 1
    
    def get_list(self):
        items = self.list.items()
        items.sort(self._sortfunc)
        return items


def echo(string):
    print string.encode("utf8")

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

hosts = Histogram()
people = Histogram()
licenses = Histogram()
components = Histogram()
mostp_name = None
mostp_count = 0
nr_binpaks = 0
nr_patches = 0
maxpy_lines = 0
maxpy_name = None
paknames = {}
dependencies = Histogram()

errors = []

paks = scan_pspec(sys.argv[1])
for pak in paks:
    spec = pisi.specfile.SpecFile()
    try:
        spec.read(os.path.join(pak, "pspec.xml"))
    except Exception, inst:
        errors.append([pak, str(inst)])
        continue
    errs = spec.has_errors()
    if errs:
        for e in errs:
            errors.append([pak, e])
        continue
    try:
        f = file(os.path.join(pak, "actions.py"))
        L = len(f.readlines())
        if L > maxpy_lines:
            maxpy_lines = L
            maxpy_name = spec.source.name
        f.close()
    except:
        pass
    nr_binpaks += len(spec.packages)
    nr_patches += len(spec.source.patches)
    paknames[spec.source.name] = 1
    add_deps(dependencies, spec)
    if len(spec.source.patches) > mostp_count:
        mostp_count = len(spec.source.patches)
        mostp_name = spec.source.name
    name = spec.source.packager.name
    lices = spec.source.license
    partof = spec.source.partof
    if partof:
        components.add(partof)
    people.add(name)
    for lice in lices:
        licenses.add(lice)
    host = pisi.uri.URI(spec.source.archiveUri).location()
    hosts.add(host)

print "<html><head><title>%s İstatistikleri</title>" % (sys.argv[1])
print '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
print "</head><body>"

print "<p>Toplam %d kod paketi, ve bunlardan oluşturulacak %d ikili paket var.</p>" % (len(paks), nr_binpaks)
echo(u"<p>Toplam peç sayısı %d</p>" % nr_patches)
if mostp_count > 0:
    echo(u"<p>En çok peçlenen yazılım %d peçle %s!</p>" % (mostp_count, mostp_name))

if maxpy_lines > 0:
    echo(u"<p>En uzun actions.py betiğine sahip yazılım %d satırla %s!</p>" % (maxpy_lines, maxpy_name))

if errors != []:
    print "<h1>Hatalar</h1><table>"
    for e in errors:
        print "<tr><td>%s</td><td>%s</td></tr>" % (e[0], e[1])
    print "</table>"
else:
    print "<p>Hata yok, tebrikler!</p>"

print "<h1>Komponentler</h1><table>"
for name,cnt in components.get_list():
    print "<tr><td>%s</td><td>%s</td></tr>" % (name, cnt)
print "</table>"

print "<h1>Paketleyiciler</h1><table>"
for name,cnt in people.get_list():
    echo("<tr><td>%s</td><td>%s</td></tr>" % (name, cnt))
print "</table>"

print "<h1>Lisanslar</h1><table>"
for name,cnt in licenses.get_list():
    print "<tr><td>%s</td><td>%s</td></tr>" % (name, cnt)
print "</table>"

echo(u"<h1>Bağımlılıklar<br>")
echo(u"<small>(italik olanlar depoda bulunmayanlar)</small></h1>")
print "<table>"
for name,cnt in dependencies.get_list():
    if paknames.has_key(name):
        print "<tr><td><b>%s</b></td><td>%d</td></tr>" % (name, cnt)
    else:
        print "<tr><td><i>%s</i></td><td>%d</td></tr>" % (name, cnt)
print "</table>"

echo(u"<h1>Kod kaynakları</h1><table>")
for name,cnt in hosts.get_list():
    print "<tr><td>%s</td><td>%s</td></tr>" % (name, cnt)
print "</table>"

print "</body>"
