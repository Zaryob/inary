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
import codecs

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

sys.path.append('.')
import pisi.specfile
import pisi.uri

# default html templates

def_table_html = u"""
<tr><td>%s</td><td>%s</td></tr>
"""

def_repo_html = u"""
<html><head>
    <title>Depo istatistikleri</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head><body>

<p>
Depoda toplam %(nr_source)d kaynak paket, ve bu paketlerden oluşturulacak
%(nr_packages)d ikili paket bulunmaktadır. Toplam %(nr_patches)d yama mevcuttur.
</p>

<p>
%(errors)s
</p>

<h3>En fazla yamalanmış 5 kaynak paket:</h3><p><table><tbody>
%(most_patched)s
</tbody></table></p>

<h3>En uzun actions.py betikli 5 kaynak paket:</h3><p><table><tbody>
%(longpy)s
</tbody></table></p>

<h3>Eksik paketler</h3><p><table><tbody>
%(missing)s
</tbody></table></p>

<h3>Paketçiler:</h3><p><table><tbody>
%(packagers)s
</tbody></table></p>


</body></html>
"""

def_packager_html = u"""
<html><head>
    <title>Paketçi %(name)s</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head><body>

<p>%(name)s &lt;%(email)s&gt;</p>
<p>Paketler:</p>
<p>%(sources)s</p>

</body></html>
"""

def_package_html = u"""
<html><head>
    <title>İkili paket %(name)s</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head><body>

<h1>İkili paket: %(name)s</h1>
<h2>Versiyon %(version)s, sürüm %(release)s</h2>

<h3>Derlemek için gerekenler:</h3>
<p>%(buildDeps)s</p>

<h3>Çalıştırmak için gerekenler:</h3>
<p>%(runtimeDeps)s</p>

<h3>Bağımlı paketler (derlenmek için):</h3>
<p>%(revBuildDeps)s</p>

<h3>Bağımlı paketler (çalışmak için):</h3>
<p>%(revRuntimeDeps)s</p>

</body></html>
"""

def_source_html = u"""
<html><head>
    <title>Kaynak paket %(name)s</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head><body>

<h1>Kaynak paket: %(name)s</h1>
<h2>Kaynak versiyon %(version)s, depo sürümü %(release)s</h2>
<h3><a href='%(homepage)s'>%(homepage)s</a></h3>

<h3>Lisanslar:</h3>
<p>%(license)s</p>

<h3>Bu kaynaktan derlenen ikili paketler:</h3>
<p>%(packages)s</p>

</body></html>
"""

def_missing_html = u"""
<html><head>
    <title>Eksik ikili paket %(name)s</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head><body>

<h1>Eksik ikili paket: %(name)s</h1>

<h3>Bağımlı paketler (derlenmek için):</h3>
<p>%(revBuildDeps)s</p>

<h3>Bağımlı paketler (çalışmak için):</h3>
<p>%(revRuntimeDeps)s</p>

</body></html>
"""


# FIXME: This check should be in specfile
valid_filetypes = [
    "executable",
    "library",
    "data",
    "config",
    "doc",
    "man",
    "info",
    "localedata",
    "header",
    "all"
]

def printu(obj):
    if isinstance(obj, unicode):
        print obj.encode('utf-8')
    elif isinstance(obj, str):
        print obj.decode('utf-8')
    else:
        print str(obj)

def valuesort(x, y):
    if x[1] > y[1]:
        return -1
    elif x[1] == y[1]:
        return 0
    else:
        return 1

def find_pspecs(folder):
    paks = []
    for root, dirs, files in os.walk(folder):
        if "pspec.xml" in files:
            paks.append(root)
        # dont walk into the versioned stuff
        if ".svn" in dirs:
            dirs.remove(".svn")
    return paks

def template_get(tmpl_name):
    try:
        f = codecs.open(tmpl_name + ".html", "r", "utf-8")
        data = f.read()
        f.close()
        return data
    except:
        return globals()["def_" + tmpl_name + "_html"]

def template_write(filename, tmpl_name, dict):
    f = codecs.open(filename, "w", "utf-8")
    f.write(template_get(tmpl_name) % dict)
    f.close()

def template_table(tmpl_name, list):
    tmpl = template_get(tmpl_name)
    data = ""
    for item in list:
        data += (tmpl % item)
    return data


class Histogram:
    def __init__(self):
        self.list = {}
    
    def add(self, name, value=None):
        if value:
            self.list[name] = value
        else:
            if self.list.has_key(name):
                self.list[name] = self.list[name] + 1
            else:
                self.list[name] = 1
    
    def get_list(self, max=0):
        items = self.list.items()
        items.sort(valuesort)
        if max != 0:
            return items[:max]
        else:
            return items


# Dictionary of all source packages keyed by the source name
sources = {}

# Dictionary of all binary packages keyed by the package name
packages = {}

# Dictionary of all packagers keyed by the packager name
packagers = {}

# Dictionary of missing depended binary packages keyed by the package name
missing = {}

# List of all repository problems
errors = []


class Missing:
    def __init__(self, name):
        missing[name] = self
        self.name = name
        self.revBuildDeps = []
        self.revRuntimeDeps = []
    
    def report_html(self):
        bDeps = map(lambda x: "<a href='package-%s.html'>%s</a>" % (x, x), self.revBuildDeps)
        rDeps = map(lambda x: "<a href='package-%s.html'>%s</a>" % (x, x), self.revRuntimeDeps)
        dict = {
            "name": self.name,
            "revBuildDeps": ", ".join(bDeps),
            "revRuntimeDeps": ", ".join(rDeps)
        }
        template_write("paksite/package-%s.html" % self.name, "missing", dict)


class Package:
    def __init__(self, source, pakspec):
        name = pakspec.name
        if packages.has_key(name):
            errors.append(_("Duplicate binary packages:\n%s\n%s\n") % (
                source.name, packages[name].source.name))
            return
        for p in pakspec.paths:
            if p.fileType not in valid_filetypes:
                e = _("Unknown file type '%s' in package '%s'") % (
                    p.fileType, source.name)
                errors.append(e)
        packages[name] = self
        self.name = name
        self.source = source
        self.pakspec = pakspec
        self.revBuildDeps = []
        self.revRuntimeDeps = []
    
    def markDeps(self):
        # mark reverse build dependencies
        for d in self.source.spec.source.buildDeps:
            p = d.package
            if packages.has_key(p):
                packages[p].revBuildDeps.append(self.name)
            else:
                if not missing.has_key(p):
                    Missing(p)
                missing[p].revBuildDeps.append(self.name)
        # mark reverse runtime dependencies
        for d in self.pakspec.runtimeDeps:
            p = d.package
            if packages.has_key(p):
                packages[p].revRuntimeDeps.append(self.name)
            else:
                if not missing.has_key(p):
                    Missing(p)
                missing[p].revRuntimeDeps.append(self.name)
    
    def report(self):
        source = self.source.spec.source
        printu(_("Binary package: %s") % self.name)
        printu(_("  Version %s release %s") % (source.version, source.release))
        printu(_("  Packager: %s <%s>") % (
            source.packager.name, source.packager.email))
        printu(_("  Build dependencies:"))
        for d in source.buildDeps:
            printu("    %s" % d.package)
        printu(_("  Runtime dependencies:"))
        for d in self.pakspec.runtimeDeps:
            printu("    %s" % d.package)
        if self.revBuildDeps:
            printu(_("  Reverse build dependencies:"))
            for d in self.revBuildDeps:
                printu("    %s" % d)
        if self.revRuntimeDeps:
            printu(_("  Reverse runtime dependencies:"))
            for d in self.revRuntimeDeps:
                printu("    %s" % d)
    
    def report_html(self):
        source = self.source.spec.source
        bDeps = map(lambda x: "<a href='package-%s.html'>%s</a>" % (x, x),
            (map(lambda x: x.package, source.buildDeps)))
        rDeps = map(lambda x: "<a href='package-%s.html'>%s</a>" % (x, x),
            (map(lambda x: x.package, self.pakspec.runtimeDeps)))
        rbDeps = map(lambda x: "<a href='package-%s.html'>%s</a>" % (x, x), self.revBuildDeps)
        rrDeps = map(lambda x: "<a href='package-%s.html'>%s</a>" % (x, x), self.revRuntimeDeps)
        dict = {
            "name": self.name,
            "version": source.version,
            "release": source.release,
            "buildDeps": ", ".join(bDeps),
            "runtimeDeps": ", ".join(rDeps),
            "revBuildDeps": ", ".join(rbDeps),
            "revRuntimeDeps": ", ".join(rrDeps)
        }
        template_write("paksite/package-%s.html" % self.name, "package", dict)


class Source:
    def __init__(self, path, spec):
        name = spec.source.name
        if sources.has_key(name):
            errors.append(_("Duplicate source packages:\n%s\n%s\n") % (
                path, sources[name].path))
            return
        sources[name] = self
        self.spec = spec
        self.name = name
        self.path = path
        for p in spec.packages:
            Package(self, p)
        self.checkRelease()
    
    def checkRelease(self):
        # FIXME: this check also belongs to specfile
        prev = None
        for h in self.spec.source.history:
            if prev:
                prev -= 1
                if prev <= 0:
                    e = _("Source package '%s' has wrong release numbers") % self.name
                    errors.append(e)
                    return
                if int(h.release) != prev:
                    e = _("Source package '%s' lacks release %d") % (self.name, prev)
                    errors.append(e)
                    return
            else:
                prev = int(h.release)
        if prev != 1:
            e = _("Source package '%s' has no first release") % self.name
            errors.append(e)
    
    def report_html(self):
        source = self.spec.source
        paks = map(lambda x: "<a href='package-%s.html'>%s</a>" % (x, x),
            (map(lambda x: x.name, self.spec.packages)))
        dict = {
            "name": self.name,
            "homepage": source.homepage,
            "license": ", ".join(source.license),
            "version": source.version,
            "release": source.release,
            "packages": ", ".join(paks)
        }
        template_write("paksite/source-%s.html" % self.name, "source", dict)


class Packager:
    def __init__(self, spec):
        name = spec.source.packager.name
        email = spec.source.packager.email
        if packagers.has_key(name):
            if email != packagers[name].email:
                e = _("Developer '%s <%s>' has another mail address '%s' in source package '%s'") % (
                    name, packagers[name].email, email, spec.source.name)
                packagers[name].errors.append(e)
                errors.append(e)
            packagers[name].sources.append(spec.source.name)
        else:
            packagers[name] = self
            self.name = name
            self.email = email
            self.sources = [spec.source.name]
            self.errors = []
    
    def report(self):
        printu(_("Packager: %s <%s>") % (self.name, self.email))
        if self.errors:
            printu(_("  Errors:"))
            for e in self.errors:
                printu("    %s" % e)
        printu(_("  Source packages (%d):") % len(self.sources))
        for s in self.sources:
            printu("    %s" % s)
    
    def report_html(self):
        srcs = map(lambda x: "<a href='source-%s.html'>%s</a>" % (x, x), self.sources)
        dict = {
            "name": self.name,
            "email": self.email,
            "sources": ", ".join(srcs)
        }
        template_write("paksite/%s.html" % self.name, "packager", dict)


class Repository:
    def __init__(self, path):
        self.path = path
        self.nr_sources = 0
        self.nr_packages = 0
        self.nr_patches = 0
        self.people = Histogram()
        self.licenses = Histogram()
        self.mostpatched = Histogram()
        self.longpy = Histogram()
        self.cscripts = Histogram()
    
    def processPspec(self, path, spec):
        # new classes
        Packager(spec)
        Source(path, spec)
        # update global stats
        self.nr_sources += 1
        self.nr_packages += len(spec.packages)
        self.nr_patches += len(spec.source.patches)
        # update top fives
        self.people.add(spec.source.packager.name)
        for p in spec.packages:
            for cs in p.providesComar:
                self.cscripts.add(cs.om)
        for L in spec.source.license:
            self.licenses.add(L)
        self.mostpatched.add(spec.source.name, len(spec.source.patches))
        try:
            f = file(os.path.join(path, "actions.py"))
            L = len(f.readlines())
            self.longpy.add(spec.source.name, L)
            f.close()
        except:
            pass
    
    def scan(self):
        for pak in find_pspecs(self.path):
            spec = pisi.specfile.SpecFile()
            try:
                spec.read(os.path.join(pak, "pspec.xml"))
            except Exception, inst:
                errors.append(_("Cannot parse '%s':\n%s\n") % (pak, inst.args[0]))
                continue
            self.processPspec(pak, spec)
        for p in packages.values():
            p.markDeps()
    
    def report(self):
        printu(_("Repository Statistics:"))
        # general stats
        printu(_("  Total of %d source packages, and %d binary packages.") % (
            self.nr_sources, self.nr_packages))
        printu(_("  There are %d patches applied.") % self.nr_patches)
        # problems
        if missing:
            printu(_("  Missing packages (%d):") % len(missing))
            for m in missing.values():
                printu("    %s" % m.name)
        # trivia
        printu(_("  Top five most patched source:"))
        for p in self.mostpatched.get_list(5):
            printu("   %4d %s" % (p[1], p[0]))
        printu(_("  Top five longest action.py scripts:"))
        for p in self.longpy.get_list(5):
            printu("   %4d %s" % (p[1], p[0]))
        # lists
        printu(_("  COMAR scripts:"))
        for cs in self.cscripts.get_list():
            printu("   %4d %s" % (cs[1], cs[0]))
        people = self.people.get_list()
        printu(_("  Packagers (%d):") % len(people))
        for p in people:
            printu("   %4d %s" % (p[1], p[0]))
        licenses = self.licenses.get_list()
        printu(_("   Licenses (%d):") % len(licenses))
        for p in licenses:
            printu("   %4d %s" % (p[1], p[0]))
    
    def report_html(self):
        miss = map(lambda x: "<tr><td><a href='./package-%s.html'>%s</a></td></tr>" % (x, x), missing.keys())
        upeople = {}
        for p in self.people.get_list():
            upeople["<a href='./%s.html'>%s</a>" % (p[0], p[0])] = p[1]
        if errors:
            e = "<br>".join(errors)
        else:
            e = ""
        upatch = {}
        for p in self.mostpatched.get_list(5):
            upatch["<a href='./source-%s.html'>%s</a>" % (p[0], p[0])] = p[1]
        ulongpy = {}
        for p in self.longpy.get_list(5):
            ulongpy["<a href='./source-%s.html'>%s</a>" % (p[0], p[0])] = p[1]
        dict = {
            "nr_source": self.nr_sources,
            "nr_packages": self.nr_packages,
            "nr_patches": self.nr_patches,
            "most_patched": template_table("table", upatch.items()),
            "longpy": template_table("table", ulongpy.items()),
            "packagers": template_table("table", upeople.items()),
            "missing": "\n".join(miss),
            "errors": e
        }
        template_write("paksite/index.html", "repo", dict)


# command line driver

if len(sys.argv) < 2:
    printu(_("Usage: repostats.py source-repo-path [ command [arg] ]"))
    sys.exit(0)

repo = Repository(sys.argv[1])
printu(_("Scanning source repository..."))
repo.scan()

if errors:
    printu("***")
    printu(_("Encountered %d errors! Fix them immediately!") % len(errors))
    for e in errors:
        printu(e)
    printu("***")

if len(sys.argv) > 2:
    if sys.argv[2] == "packager":
        if len(sys.argv) > 3:
            packagers[unicode(sys.argv[3].decode('utf-8'))].report()
            sys.exit(0)
        else:
            for p in packagers.values():
                printu(_("%s <%s>, %s source package") % (p.name, p.email, len(p.sources)))
            sys.exit(0)
    elif sys.argv[2] == "package":
        if len(sys.argv) > 3:
            packages[unicode(sys.argv[3].decode('utf-8'))].report()
            sys.exit(0)
        else:
            printu(_("Which package?"))
            sys.exit(0)
    elif sys.argv[2] == "html":
        try:
            os.mkdir("paksite")
        except:
            pass
        repo.report_html()
        for p in packagers.values():
            p.report_html()
        for p in missing.values():
            p.report_html()
        for p in packages.values():
            p.report_html()
        for p in sources.values():
            p.report_html()
        sys.exit(0)

repo.report()
