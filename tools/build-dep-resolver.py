#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# basic build dependency resolver..
#
# example usage:
#     ./build-dep-resolver.py pardus-devel/desktop/kde/


import xml.dom.minidom as mdom
import sys
import os


Get   = lambda j, w: \
          [x for x in j.childNodes \
              if x.nodeType == x.ELEMENT_NODE \
              if x.tagName == w]


def getBuildDependencies(pspec):
    dom = mdom.parse(pspec)
    try:
        return [bdep.firstChild.wholeText for bdep in Get(Get(Get(dom.documentElement, "Source")[0], "BuildDependencies")[0], 'Dependency')]
    except:
        return ['']

def getPackageNames(pspec):
    packages = []
    dom = mdom.parse(pspec)
    pspecdata = dom.documentElement
    for p in Get(pspecdata, "Package"):
        packages.append(Get(p, "Name")[0].firstChild.wholeText)
    return packages

def findPspecs():
    pspeclist = []
    for root, dirs, files in os.walk(sys.argv[1]):
        if "pspec.xml" in files:
            pspeclist.append(root + '/pspec.xml')
    return pspeclist

def buildDepResolver(pspeclist):
    """arranges the order of the pspec's in the pspeclist to satisfy build deps"""
    clean = True
    for i in range(0, pspeccount):
        pspec = pspeclist[i]
        for p in depmap.get(pspec):
            for j in range(i+1, pspeccount):
                if p in namemap.get(pspeclist[j]):
                    pspeclist.insert(j+1, pspeclist.pop(i))
                    clean = False
    if not clean:
        return False
    else:
        return pspeclist

pspeclist = findPspecs()

depmap, namemap, pspeccount = {}, {}, len(pspeclist)
for pspec in pspeclist: depmap[pspec]  = getBuildDependencies(pspec)
for pspec in pspeclist: namemap[pspec] = getPackageNames(pspec)


while not buildDepResolver(pspeclist): pass


print pspeclist
