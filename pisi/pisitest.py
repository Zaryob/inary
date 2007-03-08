#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2006, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

import os
import sys
import exceptions

import pisi
import pisi.testdb
import time


def handle_exception(exception, value, tb):
    print exception, value, tb
    if exception == exceptions.KeyboardInterrupt:
        pisi.api.finalize()
        print("\n")
        sys.exit()

def testPickle(iter):
    import cPickle
    pisi.api.init(write=True)
    
    packageNames = pisi.context.packagedb.list_packages(pisi.db.itembyrepodb.all)
    packages = {}
    totalPack =  len(packageNames)
    
    for name in packageNames:
        packages[name] = pisi.context.packagedb.get_package(name, pisi.db.itembyrepodb.all)
    
    start = time.clock()
    for i in range(iter):
        size = 0;
        for pak in packages:
            pickled = cPickle.dumps(packages[pak],1)
            size += len(pickled)
            #pisi.context.packagedb.add_package2(pak, pisi.db.itembyrepodb.installed)
            #print pak.source.name, pak.installedSize
    end = time.clock()
    delta = (end - start)
    print("Total Packages: %s" % totalPack)
    print("Total Size: %s, Average Size: %s" % (size, size / totalPack))
    print("Iterations: %s Total time: %ss. Average time :%ss." % (iter, delta , delta/iter) )
    pisi.api.finalize()

def testUnPickle(iter):
    import cPickle
    pisi.api.init(write=True)
    
    packageNames = pisi.context.packagedb.list_packages(pisi.db.itembyrepodb.all)
    packages = {}
    pickles = {}
    totalPack =  len(packageNames)
    
    for name in packageNames:
        packages[name] = pisi.context.packagedb.get_package(name, pisi.db.itembyrepodb.all)
    
    size = 0;
    for pak in packages:
        pickled = cPickle.dumps(packages[pak],1)
        pickles[pak] = pickled
            
    start = time.clock()
    for i in range(iter):
        for name in pickles:
            package = cPickle.loads(pickles[name])
    end = time.clock()
    
    delta = (end - start)
    print("Total Packages: %s" % totalPack)
    print("Iterations: %s Total time: %ss. Average time :%ss." % (iter, delta , delta/iter) )
    pisi.api.finalize()

def testDatabaseSingleTransaction():
    import cPickle
    import pisi.context as ctx
    import bsddb3.db as bsd
    from pisi.db.itembyrepodb import ItemByRepoDB

    pisi.api.init(write=True)
    
    packageNames = pisi.context.packagedb.list_packages(pisi.db.itembyrepodb.all)
    packages = {}
    totalPack =  len(packageNames)
    
    try:
        os.unlink("/var/db/pisi/package_perf.bdb")
        os.unlink("/var/db/pisi/package_perf.bdb.lock")
    except:
        pass
        
    db = ItemByRepoDB('package_perf')
    
    for name in packageNames:
        packages[name] = pisi.context.packagedb.get_package(name, pisi.db.itembyrepodb.all)
    
    start = time.time()
    txn = ctx.dbenv.txn_begin()
    for pak in packages:
        db.add_item(pak, packages[pak], pisi.db.itembyrepodb.installed, txn)
    txn.commit()
            
    end = time.time()
    
    delta = (end - start)
    print("Total Packages: %s" % totalPack)
    print("Total time: %.2f" % (delta) )
    db.close();
    pisi.api.finalize()
    
def testDatabaseFullTransaction():
    import cPickle
    import pisi.context as ctx
    import bsddb3.db as bsd
    from pisi.db.itembyrepodb import ItemByRepoDB

    pisi.api.init(write=True)
    
    packageNames = pisi.context.packagedb.list_packages(pisi.db.itembyrepodb.all)
    packages = {}
    totalPack =  len(packageNames)
    
    try:
        os.unlink("/var/db/pisi/package_perf.bdb")
        os.unlink("/var/db/pisi/package_perf.bdb.lock")
    except:
        pass
        
    db = ItemByRepoDB('package_perf')
    
    for name in packageNames:
        packages[name] = pisi.context.packagedb.get_package(name, pisi.db.itembyrepodb.all)
    
    start = time.time()
    for pak in packages:
        txn = ctx.dbenv.txn_begin()
        db.add_item(pak, packages[pak], pisi.db.itembyrepodb.installed, txn)
        txn.commit()
            
    #ctx.txn_proc(addAllPacks, None)        
    end = time.time()
    
    delta = (end - start)
    print("Total Packages: %s" % totalPack)
    print("Total time: %.2f" % (delta) )
    db.close();
    pisi.api.finalize()


def testDatabaseRead(iter):
    import cPickle
    import pisi.context as ctx
    import bsddb3.db as bsd
    from pisi.db.itembyrepodb import ItemByRepoDB

    pisi.api.init(write=True)
    
    packageNames = pisi.context.packagedb.list_packages(pisi.db.itembyrepodb.all)
    packages = {}
    totalPack =  len(packageNames)

    for name in packageNames:
        packages[name] = pisi.context.packagedb.get_package(name, pisi.db.itembyrepodb.all)
    
    try:
        os.unlink("/var/db/pisi/package_perf.bdb")
        os.unlink("/var/db/pisi/package_perf.bdb.lock")
    except:
        pass
        
    db = ItemByRepoDB('package_perf')
    
    count = 0;
    txn = ctx.dbenv.txn_begin()
    for pak in packages:
        db.add_item(pak, packages[pak], pisi.db.itembyrepodb.installed, txn)
        count += 1 
    txn.commit()
    print ( "%s packages written" % count)    
    
    start = time.time()

    for i in range(iter):
        for name in packageNames:
            package = db.get_item(name, pisi.db.itembyrepodb.all, txn)
                    
    end = time.time()
    
    delta = (end - start)
    print("Total Packages: %s" % totalPack)
    print("%s iters, Total time: %.2fs., average Time: %.2fs." % (iter, delta, delta/iter) )
    db.close();
    pisi.api.finalize()

def cleanDB():
    try:
        os.unlink("/var/db/pisi/package_perf.bdb")
        os.unlink("/var/db/pisi/package_perf.bdb.lock")
        os.unlink("/var/db/pisi/package_perf_info.bdb")
        os.unlink("/var/db/pisi/package_perf_info.lock")
        os.unlink("/var/db/pisi/package_perf_history.bdb")
        os.unlink("/var/db/pisi/package_perf_history.bdb.lock")
    except:
        pass
    

def testDatabaseSingleTransaction2(iter):
    import cPickle
    import pisi.context as ctx
    import bsddb3.db as bsd
    from pisi.db.itembyrepodb import ItemByRepoDB

    cleanDB()
    pisi.api.init(write=True)
    
    packageNames = pisi.context.packagedb.list_packages(pisi.db.itembyrepodb.all)
    packages = {}
    totalPack =  len(packageNames)

        
    dbPack = ItemByRepoDB('package_perf')
    #dbInfo = ItemByRepoDB('package_perf_info')
    dbHistory = ItemByRepoDB('package_perf_history')
    
    for name in packageNames:
        packages[name] = pisi.context.packagedb.get_package(name, pisi.db.itembyrepodb.all)
    
    print "Write test.."
    start = time.time()
    txn = ctx.dbenv.txn_begin()
    for pak in packages:
        packageDAO = pisi.testdb.PackageDAO(packages[pak])
        #packageInfoDAO = pisi.testdb.PackageInfoDAO(packages[pak])
        dbPack.add_item(pak, packageDAO, pisi.db.itembyrepodb.installed, txn)
        #dbInfo.add_item(pak, packageInfoDAO, pisi.db.itembyrepodb.installed, txn)
        dbHistory.add_item(pak, packages[pak].history, pisi.db.itembyrepodb.installed, txn)
    txn.commit()
    end = time.time()
    
    delta = (end - start)
    print("Total time: %.2f" % (delta) )

    txn = ctx.dbenv.txn_begin()
    print "read test. Read only package bodies"
    start = time.time()
    for i in range(iter):
        for name in packageNames:
            packageDAO = dbPack.get_item(name, pisi.db.itembyrepodb.all, txn)
    end = time.time()
    txn.commit()
    delta = (end - start)
    print("%s iters, Total time: %.2fs., average Time: %.2fs." % (iter, delta, delta/iter) )

    txn = ctx.dbenv.txn_begin()
    print "read test. Read only histories"
    start = time.time()
    for i in range(iter):
        for name in packageNames:
            hist = dbHistory.get_item(name, pisi.db.itembyrepodb.all, txn)
    end = time.time()
    txn.commit()
    delta = (end - start)
    print("%s iters, Total time: %.2fs., average Time: %.2fs." % (iter, delta, delta/iter) )
    
    dbPack.close()
    #dbInfo.close()
    dbHistory.close()
    pisi.api.finalize()

if __name__ == "__main__":
    sys.excepthook = handle_exception
    #testDatabaseRead(10)
    testDatabaseSingleTransaction2(20)