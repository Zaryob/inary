# -*- coding: utf-8 -*-
# PISI configuration (static and dynamic)

lib_dir_suffix = "/var/lib/pisi"
db_dir_suffix = "/var/db/pisi"
archives_dir_suffix = "/var/cache/pisi/archives"
tmp_dir_suffix =  "/var/tmp/pisi"

destdir = ''                           # install default to root by default

destdir = './test'                      # only for ALPHA

# the idea is that destdir can be set with --destdir=...

def lib_dir():
    return destdir + lib_dir_suffix

def db_dir():
    return destdir + db_dir_suffix

def archives_dir():
    return destdir + archives_dir_suffix

def tmp_dir():
    return destdir + tmp_dir_suffix
