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

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

defaultForceInstallPackageURI = "http://packages.sulin.org/main/force-install.list"

class DistUpdatePlanner:
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
        ctx.ui.info(inary.util.colorize(_("   |__  Getting index from {}").format(uri), 'blue'),noln="purple")

        try:
            if "://" in uri:
                rawdata = urllib.request.urlopen(uri).read()
            else:
                rawdata = open(uri, "r").read()
        except IOError:
            ctx.ui.info(inary.util.colorize(_("could not fetch {}".format(uri)), 'red'))
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
        ctx.ui.info(inary.util.colorize(_("   |__ Converting package objects to db object"), 'green'  ),noln=True)

        doc = ciksemel.parseString(ix)
        dbobj = inary.data.index.Index()
        dbobj.decode(doc, [])

        ctx.ui.info(inary.util.colorize(_("    done"), 'green'))
        return dbobj

    def parseRepoIndex(self):
        ctx.ui.info(inary.util.colorize(_("   |__ Parsing package properties in new repo"), 'blue'))

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

        ctx.ui.info(inary.util.colorize(_("       \_ found {0} packages and {1} obsoletelist").format(len(list(pkgprop.keys())), len(obsoletelist)), 'green' ))

        self.nextRepoPackages = pkgprop
        self.nextRepoObsoletes = obsoletelist

    def getInstalledPackages(self):
        ctx.ui.info(inary.util.colorize(_("   |__ Getting installed packages"), 'blue'))

        a = inary.reactor.list_installed()
        a.sort()

        ctx.ui.info(inary.util.colorize(_("       \_ found {} packages").format(len(a)),'green'))
        self.installedPackages = a

    def getForceInstallPackages(self):
        ctx.ui.info(inary.util.colorize(_("   |__ Getting force install packages"), 'blue'))
        pkglist=[]
        #try:
        #    pkglist = urllib.request.urlopen(self.forceInstallUri).read().split()
        #except:
        #    ctx.ui.info(inary.util.colorize(_('    [X] Not get force install packages'), 'red'))

        ctx.ui.info(inary.util.colorize(_("       \_ found {} packages".format(len(pkglist))), 'green'))
        self.forceInstallPackages = pkglist

    def calculateInstalledSize(self):
        ctx.ui.info(inary.util.colorize(_("   |__ Calculating disk space installed packages are using"), 'blue'))

        totalsize = 0
        idb = inary.db.installdb.InstallDB()

        for i in self.installedPackages:
            pkg = idb.get_package(i)
            totalsize += pkg.installedSize
            ctx.ui.debug("   %-30s %s" % (pkg.name, pkg.installedSize))

        ctx.ui.info(inary.util.colorize(_("       \_ total size = {}").format(totalsize),'cyan'))
        self.sizeOfInstalledPackages = totalsize

    def calculateNextRepoSize(self):
        ctx.ui.info(inary.util.colorize(_("   |__ Calculating package size and installed size of new packages"), 'blue'))

        for p in self.packagesToInstall:
            i = self.nextRepoPackages[p]

            self.sizeOfPackagesToDownload += i[2]
            self.sizeOfInstalledPackagesAfterUpdate += i[3]

            if i[2] > self.sizeOfBiggestPackage:
                self.sizeOfBiggestPackage = i[2]

        ctx.ui.info(inary.util.colorize(_("       \_ total download size = {}").format(self.sizeOfPackagesToDownload)), 'green')
        ctx.ui.info(inary.util.colorize(_("       \_ total install size  = {}").format(self.sizeOfInstalledPackagesAfterUpdate)), 'green')

    def calculeNeededSpace(self):
        ctx.ui.info(inary.util.colorize(_("   |__ Calculating needed space for distupate")),'blue')

        neededspace = 0
        neededspace += self.sizeOfPackagesToDownload
        neededspace += (self.sizeOfInstalledPackagesAfterUpdate - self.sizeOfInstalledPackages)
        neededspace += 2 * self.sizeOfBiggestPackage

        self.sizeOfNeededTotalSpace = neededspace
        ctx.ui.info(inary.util.colorize(_("       \_ total needed space = {}").format(neededspace)), 'green')

    def findMissingPackages(self):
        ctx.ui.info(inary.util.colorize(_("   |__ Calculating package differences of old and new repos"), 'blue'))

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

        ctx.ui.info(inary.util.colorize(_("       \_ found {} obsoleted and replaced packages").format(len(neededPackages)),'green'))
        self.missingPackages = neededPackages

    def resolveDependencies(self, A, pkgdb):
        ctx.ui.info(inary.util.colorize(_("   |__ Find dependencies for packages to be installed"), 'blue'))

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
        G_f = inary.data.pgraph.PGraph(packagedb)

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
        ctx.ui.info(inary.util.colorize(_("* Planning the whole distupdate process"), 'purple'))

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

        ctx.ui.info(inary.util.colorize(_("    done"), 'green'))
        ctx.ui.info(inary.util.colorize(_("       \_ found {} packages to install".format(len(self.packagesToInstall))), 'green'))

    def plan(self):
        ctx.ui.info(inary.util.colorize(_("* Find missing packages for dist-update "), 'purple'))

        self.getIndex()
        self.parseRepoIndex()
        self.getInstalledPackages()
        self.calculateInstalledSize()
        self.findMissingPackages()
        self.planDistUpdate()
        self.calculateNextRepoSize()
        self.calculeNeededSpace()

def MakeDistUpdate(packages=None):
    try:
        inary.operations.upgrade.upgrade(packages, 'distuprepo') #FIXME: Should write a detailed
                                                                 # upgrade system
    except:
        raise Error(_('A problem occured')) # FIXME: When not complete distupdate
                                            # inary make takeback
