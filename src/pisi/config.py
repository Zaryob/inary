# -*- coding: utf-8 -*-
# PISI configuration (static and dynamic)

lib_dir_suffix = "/var/lib/pisi"
db_dir_suffix = "/var/db/pisi"
archives_dir_suffix = "/var/cache/pisi/archives"
tmp_dir_suffix =  "/var/tmp/pisi"

# directory suffixes for build
# I'm not comfortable with these and accompanying functions,
# but could find a cleaner way for now.
build_work_dir_suffix = "/work"
build_install_dir_suffix  = "/install"


destdir = ''                           # install default to root by default

destdir = './tmp'                      # only for ALPHA

# the idea is that destdir can be set with --destdir=...

def lib_dir():
    return destdir + lib_dir_suffix

def db_dir():
    return destdir + db_dir_suffix

def archives_dir():
    return destdir + archives_dir_suffix

def tmp_dir():
    return destdir + tmp_dir_suffix

def build_work_dir(packageName, version, release):
    packageDir = packageName + '-' + version + '-' + release
    return destdir + '/' + packageDir + build_work_dir_suffix

def build_install_dir(packageName, version, release):
    packageDir = packageName + '-' + version + '-' + release
    return destdir + '/' + packageDir + build_install_dir_suffix
