#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Dist Update planner using inary api and ciksemel
# This script resides because we need to check if we can
# update, to find out what is missing for update etc.
# without adding new distro repo / upgrading any packages
#

import os
import sys

import bz2
import lzma 
import urllib.request, urllib.error, urllib.parse

import ciksemel
import inary
import inary.context as ctx

defaultForceInstallPackageURI = "http://packages.sulin.org/main/force-install.list"

class DistupdatePlanner:
    def __init__(self, nextRepoUri, forceInstallUri=defaultForceInstallPackageURI, Debug=False):
        self.debug = Debug
        self.forceInstallUri = forceInstallUri
        self.nextRepoUri = nextRepoUri

        self.nextRepoRaw = None
        self.nextRepoPackages = {}
        self.nextRepoReplaces = {}
        self.nextRepoObsoletes = []

        self.installedPackages = []
        self.packagesToInstall = []
        self.forceInstallPackages = []
        self.missingPackages = []
        self.graphobj = None

        self.sizeOfInstalledPackages = 0
        self.sizeOfInstalledPackagesAfterUpdate = 0
        self.sizeOfPackagesToDownload = 0
        self.sizeOfBiggestPackage = 0
        self.sizeOfNeededTotalSpace = 0

    def uniq(self, i):
        return list(set(i))

    def getIndex(self):
        uri = self.nextRepoUri
        ctx.ui.info(_("* Getting index from {}").format(uri))

        try:
            if "://" in uri:
                rawdata = urllib.request.urlopen(uri).read()
            else:
                rawdata = open(uri, "r").read()
        except IOError:
            ctx.ui.info("could not fetch {}".format(uri))
            return None

        if uri.endswith("bz2"):
            data = bz2.decompress(rawdata)
        elif uri.endswith("xz") or uri.endswith("lzma"):
            data = lzma.decompress(rawdata)
        else:
            data = rawdata

        ctx.ui.info(_("    done"))
        self.nextRepoRaw = data

    def convertToInaryRepoDB(self, ix):
        ctx.ui.info(_("* Converting package objects to db object"),noln=True)

        doc = ciksemel.parseString(ix)
        dbobj = inary.index.Index()
        dbobj.decode(doc, [])

        ctx.ui.info("    done")
        return dbobj

    def parseRepoIndex(self):
        ctx.ui.info(_("* Parsing package properties in new repo"))

        pkgprop = {}
        obsoletelist = []
        ix = ciksemel.parseString(self.nextRepoRaw)

        obsoleteParent = ix.getTag("Distribution").getTag("Obsoletes")
        for node in obsoleteParent.tags("Package"):
            obsoletelist.append(node.firstChild().data())

        for i in ix.tags("Package"):
            replaceslist = []

            pkgName = i.getTagData("Name")
            pkgURI = i.getTagData("PackageURI")
            pkgSize = int(i.getTagData("PackageSize"))
            pkgHash = i.getTagData("PackageHash")
            pkgInstalledSize = int(i.getTagData("InstalledSize"))

            replacedPackages = i.getTag("Replaces")

            if replacedPackages:
                for replaced in replacedPackages.tags("Package"):
                    replaceslist.append(replaced.firstChild().data())

            pkgprop[pkgName] = [replaceslist, pkgURI, pkgSize, pkgInstalledSize, pkgHash]

        ctx.ui.info(_("    found {0} packages and {1} obsoletelist").format(len(list(pkgprop.keys())), len(obsoletelist)))

        self.nextRepoPackages = pkgprop
        self.nextRepoObsoletes = obsoletelist

    def getInstalledPackages(self):
        ctx.ui.info(_("* Getting installed packages"))

        a = inary.reactor.list_installed()
        a.sort()

        ctx.ui.info(_("    found {} packages").format(len(a)))
        self.installedPackages = a

    def getForceInstallPackages(self):
        ctx.ui.info(_("* Getting force install packages"))

        pkglist = urllib.request.urlopen(self.forceInstallUri).read().split()

        ctx.ui.info(_("    found {} packages").format(len(pkglist)))
        self.forceInstallPackages = pkglist

    def calculateInstalledSize(self):
        ctx.ui.info(_("* Calculating disk space installed packages are using"))

        totalsize = 0
        idb = inary.db.installdb.InstallDB()

        for i in self.installedPackages:
            pkg = idb.get_package(i)
            totalsize += pkg.installedSize
            #print "%-30s %s" % (pkg.name, pkg.installedSize)

        ctx.ui.info(_("    total size = {}").format(totalsize))
        self.sizeOfInstalledPackages = totalsize

    def calculateNextRepoSize(self):
        ctx.ui.info(_("* Calculating package size and installed size of new packages"))

        for p in self.packagesToInstall:
            i = self.nextRepoPackages[p]

            self.sizeOfPackagesToDownload += i[2]
            self.sizeOfInstalledPackagesAfterUpdate += i[3]

            if i[2] > self.sizeOfBiggestPackage:
                self.sizeOfBiggestPackage = i[2]

        ctx.ui.info(_("    total download size = {}").format(self.sizeOfPackagesToDownload))
        ctx.ui.info(_("    total install size  = {}").format(self.sizeOfInstalledPackagesAfterUpdate))

    def calculeNeededSpace(self):
        ctx.ui.info(_("* Calculating needed space for distupate"))

        neededspace = 0
        neededspace += self.sizeOfPackagesToDownload
        neededspace += (self.sizeOfInstalledPackagesAfterUpdate - self.sizeOfInstalledPackages)
        neededspace += 2 * self.sizeOfBiggestPackage

        self.sizeOfNeededTotalSpace = neededspace
        ctx.ui.info(_("    total needed space = {}").format(neededspace))

    def findMissingPackages(self):
        ctx.ui.info(_("* Calculating package differences of old and new repos"))

        pkglist = []
        replacedBy = {}
        neededPackages = []

        # we make a cache of replaced packages, not to iterate over and over on package dict
        for i in self.nextRepoPackages:
            pkglist.append(i)
            for r in self.nextRepoPackages[i][0]:
                pkglist.append(r)
                if r in replacedBy:
                    replacedBy[r].append(i)
                else:
                    replacedBy[r] = [i]

        self.nextRepoReplaces = replacedBy

        # and we package list of removed (replaced + obsoleted) packages
        pkglist.extend(self.nextRepoObsoletes)
        uniqpkglist = self.uniq(pkglist)

        for i in self.installedPackages:
            if i not in uniqpkglist:
                neededPackages.append(i)

        ctx.ui.info(_("    found {} obsoleted and replaced packages").format(len(neededPackages)))
        self.missingPackages = neededPackages

    def resolveDependencies(self, A, pkgdb):
        ctx.ui.info(_("* Find dependencies for packages to be installed"))

        # this would be the system package db on a normal scenario
        # packagedb = inary.db.packagedb.PackageDB()

        repodict = dict((pkg.name, pkg) for pkg in pkgdb.packages)

        # our lovely fake package db, we need to make up one since
        # we are working on a repository that is not added to system
        class PackageDB:
            def get_package(self, key, repo = None):
                return repodict[str(key)]

        packagedb = PackageDB()

        # write package names as a list for testing
        # A = repodict.keys()

        # construct G_f
        G_f = inary.pgraph.PGraph(packagedb)

        # find the install closure graph of G_f by package
        # set A using packagedb
        for x in A:
            G_f.add_package(x)

        B = A
        while len(B) > 0:
            Bp = set()
            for x in B:
                pkg = packagedb.get_package(x)
                for dep in pkg.runtimeDependencies():

                    if not dep.package in G_f.vertices():
                        Bp.add(str(dep.package))
                    G_f.add_dep(x, dep)

            B = Bp

        installOrder = G_f.topological_sort()
        installOrder.reverse()

        return G_f, installOrder


    def planDistUpdate(self):
        ctx.ui.info(_("* Planning the whole distupdate process"))

        # installed packages
        currentPackages = self.installedPackages

        toRemove = []
        toAdd = []

        # handle replaced packages
        for i in currentPackages:
            if i in self.nextRepoReplaces:
                toRemove.append(i)
                toAdd.extend(self.nextRepoReplaces[i])

        # remove "just obsoleted" packages
        toRemove.extend(self.nextRepoObsoletes)

        # this should never happen with normal usage, yet we need to calculate the scenario
        toRemove.extend(self.missingPackages)

        # new packages needed for the new distro version
        self.getForceInstallPackages()
        toAdd.extend(self.forceInstallPackages)

        currentPackages.extend(toAdd)
        currentPackages = list(set(currentPackages) - set(toRemove))

        indexstring = self.nextRepoRaw
        repodb = self.convertToInaryRepoDB(indexstring)

        self.graphobj, self.packagesToInstall = self.resolveDependencies(currentPackages, repodb)

        ctx.ui.info("    found {} packages to install".format(len(self.packagesToInstall)))

    def plan(self):
        ctx.ui.info(_("* Find missing packages for distupdate "))

        self.getIndex()
        self.parseRepoIndex()
        self.getInstalledPackages()
        self.calculateInstalledSize()
        self.findMissingPackages()
        self.planDistUpdate()
        self.calculateNextRepoSize()
        self.calculeNeededSpace()

class MakeDistUpdate():
    pass
