#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2007, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#

import sys
import os
import codecs
import re
import getopt

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

from svn import core, client

sys.path.append('.')
import pisi.specfile
import pisi.uri
import pisi.package
import pisi.metadata
import pisi.files
from pisi.cli import printu

# Main HTML template

html_header = """
<html><head>
    <title>%(title)s</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <link href="http://www.pardus.org.tr/styles/stil.css" rel="stylesheet" type="text/css">
</head><body>
<div id='header-bugzilla'>
</div>

<div class='statmenu'>
<a href='%(root)sindex.html'>Genel Bilgiler</a>
 | <a href='%(root)ssources.html'>Kaynak Paketler</a>
 | <a href='%(root)sbinaries.html'>İkili Paketler</a>
 | <a href='%(root)spackagers.html'>Paketçiler</a>
</div>

<hr>

<h1 align='center'>%(title)s</h1>

<div id='content'>
%(content)s
</div>

</body></html>
"""








# default html templates

def_table_html = u"""
<tr><td>%s</td><td>%s</td></tr>
"""

def_repo_sizes_html = u"""
<h3>Boyutlar</h3>
<p>Toplam kurulu boyut %(total)s</p>
<p>Dosya tiplerine göre liste:</p>
<table><tbody>
%(sizes)s
</table></tbody>
"""

def_package_html = u"""
<html><head>
    <title>İkili paket %(name)s</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <link href="http://www.pardus.org.tr/styles/stil.css" rel="stylesheet" type="text/css">

</head><body>
<div id="header-bugzilla">
</div>
<div id="packets">

<h1>İkili paket: %(name)s</h1>
<h2>Kaynak versiyon %(version)s, depo sürümü %(release)s</h2>

<h3>Kaynak paket <a href="../source/%(source)s.html">%(source)s</a></h3>

<h3>Derlemek için gerekenler:</h3>
<p>%(buildDeps)s</p>

<h3>Çalıştırmak için gerekenler:</h3>
<p>%(runtimeDeps)s</p>

<h3>Bağımlı paketler (derlenmek için):</h3>
<p>%(revBuildDeps)s</p>

<h3>Bağımlı paketler (çalışmak için):</h3>
<p>%(revRuntimeDeps)s</p>
</div>
</body></html>
"""

def_history_html= u"""
<h5>Sürüm %s</h5><p>
Tarih: %s<br>
Yapan: <a href="../packager/%s.html">%s</a><br>
Açıklama: %s
</p>
"""

def_source_html = u"""
<html><head>
    <title>Kaynak paket %(name)s</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <link href="http://www.pardus.org.tr/styles/stil.css" rel="stylesheet" type="text/css">

</head><body>
<div id="header-bugzilla">
</div>
<div id="packets">

<h1>Kaynak paket: %(name)s</h1>
<h2>Kaynak versiyon %(version)s, depo sürümü %(release)s</h2>
<h3><a href='%(homepage)s'>%(homepage)s</a></h3>

<h3>Açıklama</h3>
<p>%(summary)s</p>

<h3>Lisanslar:</h3>
<p>%(license)s</p>

<h3>İşlemler:</h3>
<p><a href="%(uri)s">Paket dosyalarına bak</a></p>
<p><a href="http://bugs.uludag.org.tr/buglist.cgi?product=Paketler&component=%(name)s&bug_status=NEW&bug_status=ASSIGNED&bug_status=REOPENED">
Hata kayıtlarına bak</a></p>

<h3>Bu kaynaktan derlenen ikili paketler:</h3>
<p>%(packages)s</p>

<h3>Tarihçe</h3>
%(history)s

<h3>Yamalar</h3>
%(patches)s
</div>
</body></html>
"""

def_sources_html = u"""
<html><head>
    <title>Kaynak paketler listesi</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <link href="http://www.pardus.org.tr/styles/stil.css" rel="stylesheet" type="text/css">

</head><body>
<div id="header-bugzilla">
</div>
<div id="packets">

<h1>Kaynak paketler listesi</h1>
<hr>

<p>
%(source_list)s
</p>
</div>
</body></html>
"""

def_missing_html = u"""
<html><head>
    <title>Eksik ikili paket %(name)s</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <link href="http://www.pardus.org.tr/styles/stil.css" rel="stylesheet" type="text/css">

</head><body>
<div id="header-bugzilla">
</div>
<div id="packets">

<h1>Eksik ikili paket: %(name)s</h1>

<h3>Bağımlı paketler (derlenmek için):</h3>
<p>%(revBuildDeps)s</p>

<h3>Bağımlı paketler (çalışmak için):</h3>
<p>%(revRuntimeDeps)s</p>
</div>
</body></html>
"""


def svn_uri(path):
    # init
    core.apr_initialize()
    pool = core.svn_pool_create(None)
    core.svn_config_ensure(None, pool)
    # get commit date
    uri = client.svn_client_url_from_path(path, pool)
    # cleanup
    core.svn_pool_destroy(pool)
    core.apr_terminate()
    return uri


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

def write_html(filename, title, content):
    f = codecs.open(filename, "w", "utf-8")
    root = "./"
    if len(filename.split("/")) > 2:
        root = "../"
    dict = {
        "title": title,
        "content": content,
        "root": root,
    }
    f.write(html_header % dict)
    f.close()

def make_table(elements, titles=None):
    def make_row(element):
        return "<td>%s" % "<td>".join(map(str, element))
    
    title_html = ""
    if titles:
        title_html = """
            <thead><tr><th>%s</tr></thead>
        """ % "<th>".join(titles)
    
    html = """
        <table>%s<tbody>
        <tr>%s
        </tbody></table>
    """ % (title_html, "<tr>".join(map(make_row, elements)))
    
    return html

def make_url(name, path="./"):
    if not path.endswith("/"):
        path += "/"
    return "<a href='%s%s.html'>%s</a>" % (path, name, name)

def template_table(tmpl_name, list):
    tmpl = template_get(tmpl_name)
    data = ""
    for item in list:
        data += (tmpl % item)
    return data

def mangle_email(email):
    return re.sub("@", " [at] ", email)


class Histogram:
    def __init__(self):
        self.list = {}
    
    def add(self, name, value=None):
        if value:
            self.list[name] = value
        else:
            self.list[name] = self.list.get(name, 0) + 1
    
    def note(self, name):
        if not self.list.has_key(name):
            self.list[name] = 0
    
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
        bDeps = map(lambda x: "<a href='./%s.html'>%s</a>" % (x, x), self.revBuildDeps)
        rDeps = map(lambda x: "<a href='./%s.html'>%s</a>" % (x, x), self.revRuntimeDeps)
        dict = {
            "name": self.name,
            "revBuildDeps": ", ".join(bDeps),
            "revRuntimeDeps": ", ".join(rDeps)
        }
        template_write("paksite/binary/%s.html" % self.name, "missing", dict)


class Package:
    def __init__(self, source, pakspec):
        name = pakspec.name
        if packages.has_key(name):
            errors.append(_("Duplicate binary packages:\n%s\n%s\n") % (
                source.name, packages[name].source.name))
            return
        packages[name] = self
        self.name = name
        self.source = source
        self.pakspec = pakspec
        self.revBuildDeps = []
        self.revRuntimeDeps = []
        self.installedSize = 0
    
    def markDeps(self):
        # mark reverse build dependencies
        for d in self.source.spec.source.buildDependencies:
            p = d.package
            if packages.has_key(p):
                packages[p].revBuildDeps.append(self.name)
            else:
                if not missing.has_key(p):
                    Missing(p)
                missing[p].revBuildDeps.append(self.name)
        # mark reverse runtime dependencies
        for d in self.pakspec.packageDependencies:
            p = d.package
            if packages.has_key(p):
                packages[p].revRuntimeDeps.append(self.name)
            else:
                if not missing.has_key(p):
                    Missing(p)
                missing[p].revRuntimeDeps.append(self.name)
    
    def report_html(self):
        source = self.source.spec.source
        bDeps = map(lambda x: "<a href='./%s.html'>%s</a>" % (x, x),
            (map(lambda x: x.package, source.buildDependencies)))
        rDeps = map(lambda x: "<a href='./%s.html'>%s</a>" % (x, x),
            (map(lambda x: x.package, self.pakspec.packageDependencies)))
        rbDeps = map(lambda x: "<a href='./%s.html'>%s</a>" % (x, x), self.revBuildDeps)
        rrDeps = map(lambda x: "<a href='./%s.html'>%s</a>" % (x, x), self.revRuntimeDeps)
        dict = {
            "name": self.name,
            "source": source.name,
            "version": self.source.spec.getSourceVersion(),
            "release": self.source.spec.getSourceRelease(),
            "buildDeps": ", ".join(bDeps),
            "runtimeDeps": ", ".join(rDeps),
            "revBuildDeps": ", ".join(rbDeps),
            "revRuntimeDeps": ", ".join(rrDeps)
        }
        template_write("paksite/binary/%s.html" % self.name, "package", dict)


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
        self.uri = svn_uri(path)
        for p in spec.packages:
            Package(self, p)
    
    def report_html(self):
        source = self.spec.source
        paks = map(lambda x: "<a href='../binary/%s.html'>%s</a>" % (x, x),
            (map(lambda x: x.name, self.spec.packages)))
        histdata = map(lambda x: (x.release, x.date, x.name, x.name, x.comment), self.spec.history)
        ptch = map(lambda x: "<a href='%s/files/%s'>%s</a>" % (self.uri,
            x.filename, x.filename), source.patches)
        dict = {
            "name": self.name,
            "homepage": source.homepage,
            "license": ", ".join(source.license),
            "version": self.spec.getSourceVersion(),
            "release": self.spec.getSourceRelease(),
            "history": template_table("history", histdata),
            "packages": "<br>".join(paks),
            "summary": source.summary,
            "patches": "<br>".join(ptch),
            "uri": self.uri
        }
        template_write("paksite/source/%s.html" % self.name, "source", dict)


class Packager:
    def __init__(self, spec, update=None):
        if update:
            name = update.name
            email = update.email
        else:
            name = spec.source.packager.name
            email = spec.source.packager.email
        if packagers.has_key(name):
            if email != packagers[name].email:
                e = _("Developer '%s <%s>' has another mail address '%s' in source package '%s'") % (
                    name, packagers[name].email, email, spec.source.name)
                packagers[name].errors.append(e)
                errors.append(e)
            if update:
                packagers[name].updates.append((spec.source.name, update.release, update.comment))
            else:
                packagers[name].sources.append(spec.source.name)
        else:
            packagers[name] = self
            self.name = name
            self.email = email
            if update:
                self.sources = []
                self.updates = [(spec.source.name, update.release, update.comment)]
            else:
                self.sources = [spec.source.name]
                self.updates = []
            self.errors = []
        if not update:
            for update in spec.history:
                Packager(spec, update)
    
    def report_html(self):
        srcs = map(lambda x: ("<a href='../source/%s.html'>%s</a>" % (x, x), ), self.sources)
        srcs.sort()
        upds = map(lambda x: (u"<b><a href='../source/%s.html'>%s</a> (%s)</b><br>%s<br>" % (
            x[0], x[0], x[1], x[2]), ), self.updates)
        
        html = """
            <p>Paketçi: %s (%s)</p>
        """ % (self.name, mangle_email(self.email))
        
        html += """
            <div class='statstat'>
            <h3>Sahip olduğu paketler:</h3><p>
            %s
            </p></div>
        """ % make_table(srcs)
        
        html += """
            <div class='statstat'>
            <h3>Yaptığı güncellemeler:</h3><p>
            %s
            </p></div>
        """ % make_table(upds)
        
        write_html("paksite/packager/%s.html" % self.name, self.name, html)


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
        self.total_installed_size = 0
        self.installed_sizes = {}
    
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
        for u in spec.history:
            self.people.note(u.name)
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
    
    def processPisi(self, path):
        p = pisi.package.Package(path)
        p.extract_files(["metadata.xml", "files.xml"], ".")
        md = pisi.metadata.MetaData()
        md.read("metadata.xml")
        self.total_installed_size += md.package.installedSize
        if packages.has_key(md.package.name):
            # FIXME: check version/release match too?
            packages[md.package.name].installed_size = md.package.installedSize
        else:
            printu("Binary package '%s' has no source package in repository %s\n" % (path, self.path))
        fd = pisi.files.Files()
        fd.read("files.xml")
        for f in fd.list:
            if self.installed_sizes.has_key(f.type):
                # Emtpy directories and symlinks has None size
                if not f.size is None:
                    self.installed_sizes[f.type] += int(f.size)
            else:
                self.installed_sizes[f.type] = int(f.size)
    
    def scan_bins(self, binpath):
        for root, dirs, files in os.walk(binpath):
            for fn in files:
                if fn.endswith(".pisi"):
                    self.processPisi(os.path.join(root, fn))
    
    def report_html(self):
        table = (
            ("Kaynak paket sayısı", self.nr_sources),
            ("İkili paket sayısı", self.nr_packages),
            ("Yama sayısı", self.nr_patches),
            ("Paketçi sayısı", len(self.people.list)),
        )
        html = make_table(table)
        
        html += """
            <div class='statstat'>
            <h3>En fazla yamalanmış beş kaynak paket:</h3><p>
            %s
            </p></div>
        """ % make_table(self.mostpatched.get_list(5))
        
        html += """
            <div class='statstat'>
            <h3>En uzun inşa betikli beş kaynak paket:</h3><p>
            %s
            </p></div>
        """ % make_table(self.longpy.get_list(5))
        
        write_html("paksite/index.html", "Depo İstatistikleri", html)
        
        titles = (
            "<a href='packagers_by_name.html'>Paketçi</a>",
            "<a href='packagers.html'>Paket sayısı</a>"
        )
        
        people = self.people.get_list()
        people = map(lambda x: ("<a href='./packager/%s.html'>%s</a>" % (x[0], x[0]), x[1]), people)
        write_html("paksite/packagers.html", "Paketçiler (paket sayısına göre)", make_table(people, titles))
        
        people.sort(key=lambda x: x[0])
        write_html("paksite/packagers_by_name.html", "Paketçiler (isme göre)", make_table(people, titles))
        
        titles = "Paket adı", "Versiyon", "Açıklama"
        
        srclist = map(lambda x: (make_url(x.name, "source/"), x.spec.getSourceVersion(), x.spec.source.summary), sources.values())
        srclist.sort(key=lambda x: x[0])
        html = make_table(srclist, titles)
        write_html("paksite/sources.html", "Kaynak Paketler", html)
        
        binlist = map(lambda x: (make_url(x.name, "binary/"), x.source.spec.getSourceVersion(), x.source.spec.source.summary), packages.values())
        binlist.sort(key=lambda x: x[0])
        html = make_table(binlist, titles)
        write_html("paksite/binaries.html", "İkili Paketler", html)


# command line driver

def usage():
    printu(_("Usage: repostats.py [OPTIONS] source-repo-path [binary-repo-path]\n"))
    printu("  -t, --test-only:    %s" % _("Dont generate the web site.\n"))
    sys.exit(0)

if __name__ == "__main__":
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "ht", ["help", "test-only"])
    except:
        usage()
    
    if args == []:
        usage()
    
    do_web = True
    
    for o, v in opts:
        if o in ("-h", "--help"):
            usage()
        if o in ("-t", "--test-only"):
            do_web = False
    
    repo = Repository(args[0])
    printu(_("Scanning source repository...\n"))
    repo.scan()
    
    if len(args) > 1:
        printu(_("Scanning binary packages...\n"))
        repo.scan_bins(args[1])
    
    if do_web:
        if not os.path.exists("paksite/packager"):
            os.makedirs("paksite/packager")
        if not os.path.exists("paksite/binary"):
            os.makedirs("paksite/binary")
        if not os.path.exists("paksite/source"):
            os.makedirs("paksite/source")
        
        repo.report_html()
        for p in packagers.values():
            p.report_html()
        for p in missing.values():
            p.report_html()
        for p in packages.values():
            p.report_html()
        for p in sources.values():
            p.report_html()
