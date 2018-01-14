#! /usr/bin/python
# a script to preare INARY source tarball from svn
# author: exa

#TODO: arguments for svn snapshot with rev number, or a tag to override default

import sys
import os
import shutil

def run(cmd):
    print(('running', cmd))
    os.system(cmd)

sys.path.insert(0, '.')
import inary
if not os.path.exists('svndist'):
    os.makedirs('svndist')
    
ver = inary.__version__

if os.path.exists('svndist/inary-%s' % ver):
    shutil.rmtree('svndist/inary-%s' % ver)
    
print('Exporting svn directory')
run('svn export http://svn.uludag.org.tr/uludag/trunk/inary svndist/inary-%s' % ver)

os.chdir('svndist')
run('tar cjvf inary-%s.tar.bz2 inary-%s' % (ver, ver))

print('Have a look at svndist directory')
