#! /usr/bin/env python3
#
# a script to prepare INARY source tarball from any svn directory you specify
#   in any revision you want.
# author: sdalgic
#
# any comments and feedbacks are welcomed : dalgic.srdr [AT] gmail [DOT] com
#
# inspired from http://svn.pardus.org.tr/uludag/trunk/inary/tools/svndist.py written by exa.

import sys
import os
import shutil
import datetime
import inary

from optparse import OptionParser

def run(cmd):
    print(('running', cmd))
    os.system(cmd)

if __name__ == "__main__":

    sys.path.insert(0, '.')
    ver = inary.__version__
    inarySVNpath = "http://svn.uludag.org.tr/uludag/trunk/inary"
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

    parser.add_option("-p", "--path", dest="inarySVNpath", default=inarySVNpath, type="string",
                        help="Select the SVN Path which is going to be exported. It can be a local copy too. \
                                Default is http://svn.uludag.org.tr/uludag/trunk/inary ")

    parser.add_option("--with-date", action="store_true", dest="date", default=False,
                        help="Add date tag to the tar file name. ")

    (opts, args) = parser.parse_args()

    print('Exporting svn directory')

    if not os.path.exists(opts.svndist):
        os.makedirs(opts.svndist)

    if opts.rev == "HEAD":
        if os.path.exists(opts.svndist+'/inary-%s' % ver):
            shutil.rmtree(svndist+'/inary-%s' % ver)

        run('svn export %s %s/inary-%s' % (opts.inarySVNpath, opts.svndist, ver))

        os.chdir(opts.svndist)
        run('tar cjvf inary-%s.tar.bz2 inary-%s' % (ver,ver))

        if opts.date == True :
            time = datetime.datetime.now()
            os.rename('inary-%s.tar.bz2' % ver , 'inary-%s.%s.%s-%s.tar.bz2' % (time.year, time.month, time.day, ver))

    else:
        if os.path.exists(opts.svndist+'/inary-r%s' % opts.rev):
            shutil.rmtree(opts.svndist+'/inary-r%s' % opts.rev)

        run('svn export -r %s %s %s/inary-r%s' % (opts.rev, opts.inarySVNpath, opts.svndist, opts.rev))
        os.chdir(opts.svndist)
        run('tar cjvf inary-r%s.tar.bz2 inary-r%s' % (opts.rev,opts.rev))

        if opts.date == True :
            time = datetime.datetime.now()
            os.rename('inary-r%s.tar.bz2' % opts.rev , 'inary-r%s-%s.%s.%s.tar.bz2' % (opts.rev, time.year, time.month, time.day))

    print(('Have a look at %s directory' % opts.svndist))

