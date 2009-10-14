#! /usr/bin/python
#
# a script to prepare PiSi source tarball from any svn directory you specify
#   in any revision you want.
# author: sdalgic
#
# any comments and feedbacks are welcomed : dalgic.srdr [AT] gmail [DOT] com
#
# inspired from http://svn.pardus.org.tr/uludag/trunk/pisi/tools/svndist.py written by exa.

import sys
import os
import shutil
import datetime
import pisi

from optparse import OptionParser

def run(cmd):
    print 'running', cmd
    os.system(cmd)

if __name__ == "__main__":

    sys.path.insert(0, '.')
    ver = pisi.__version__
    pisiSVNpath = "http://svn.uludag.org.tr/uludag/trunk/pisi"
    svndist = "svndist"

    usage = "usage: %s [options] " % os.path.basename(sys.argv[0])
    parser = OptionParser(usage = usage)

    parser.add_option("-r", "--revision", dest="rev", default = "HEAD",
                        help="Select a revision to export. \
                                Default is the HEAD value. \
                                ")

    parser.add_option("-o", "--out-dir", dest="svndist", default = svndist, type="string",
                        help="Select the output directory to export. \
                                Default is the `svndist` directory. ")

    parser.add_option("-p", "--path", dest="pisiSVNpath", default=pisiSVNpath, type="string",
                        help="Select the SVN Path which is going to be exported. It can be a local copy too. \
                                Default is http://svn.uludag.org.tr/uludag/trunk/pisi ")

    parser.add_option("--with-date", action="store_true", dest="date", default=False,
                        help="Add date tag to the tar file name. ")

    (opts, args) = parser.parse_args()

    print 'Exporting svn directory'

    if not os.path.exists(opts.svndist):
        os.makedirs(opts.svndist)

    if opts.rev == "HEAD":
        if os.path.exists(opts.svndist+'/pisi-%s' % ver):
            shutil.rmtree(svndist+'/pisi-%s' % ver)

        run('svn export %s %s/pisi-%s' % (opts.pisiSVNpath, opts.svndist, ver))

        os.chdir(opts.svndist)
        run('tar cjvf pisi-%s.tar.bz2 pisi-%s' % (ver,ver))

        if opts.date == True :
            time = datetime.datetime.now()
            os.rename('pisi-%s.tar.bz2' % ver , 'pisi-%s.%s.%s-%s.tar.bz2' % (time.year, time.month, time.day, ver))

    else:
        if os.path.exists(opts.svndist+'/pisi-r%s' % opts.rev):
            shutil.rmtree(opts.svndist+'/pisi-r%s' % opts.rev)

        run('svn export -r %s %s %s/pisi-r%s' % (opts.rev, opts.pisiSVNpath, opts.svndist, opts.rev))
        os.chdir(opts.svndist)
        run('tar cjvf pisi-r%s.tar.bz2 pisi-r%s' % (opts.rev,opts.rev))

        if opts.date == True :
            time = datetime.datetime.now()
            os.rename('pisi-r%s.tar.bz2' % opts.rev , 'pisi-r%s-%s.%s.%s.tar.bz2' % (opts.rev, time.year, time.month, time.day))

    print 'Have a look at %s directory' % opts.svndist

