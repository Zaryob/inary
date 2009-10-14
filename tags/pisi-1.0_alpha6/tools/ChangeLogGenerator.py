#!/usr/bin/python
# -*- conding: utf-8 -*-

import os
import sys
import datetime

sys.path.append('.')

import pisi.specfile

def scanPSPEC(folder):
    packages = []
    for root, dirs, files in os.walk(folder):
        if "pspec.xml" in files:
            packages.append(root)
        # dont walk into the versioned stuff
        if ".svn" in dirs:
            dirs.remove(".svn")
    return packages

if __name__ == "__main__":
    try:
        packages = scanPSPEC(sys.argv[1])
    except:
        print "Usage: ChangeLogGenerator.py path2repo"
        sys.exit(1)

    for package in packages: 
        spec = pisi.specfile.SpecFile()
        spec.read(os.path.join(package, "pspec.xml"))

        name = spec.source.name.encode('utf-8')
        version =  spec.source.history[0].version.encode('utf-8')
        date = spec.source.history[0].date.encode('utf-8')
        packager = spec.source.packager.name.encode('utf-8')
        mail = spec.source.packager.email.encode('utf-8')
        
        try:
            year, month, day = date.split("-")
            n = datetime.date(int(year), int(month), int(day))
        except ValueError, e:
            print "Package %s: Wrong Format:" % name
            
        date = n.strftime("%d %b %Y")

        log='''# ChangeLog for %s
# Copyright © 2005 TUBITAK/UEKAE
# Licensed under the GNU General Public License, version 2.

* %s-%s (%s)

  %s; %s <%s>
  Initial import
''' % (name, name, version, date, date, packager,mail)
    
        file = os.path.join(package, "ChangeLog")
        
        if not os.path.exists(file):
            dest = open(file, "w")
            dest.write(log)
            dest.close()
