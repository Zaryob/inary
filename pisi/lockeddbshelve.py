# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
#
# Authors:  Eray Ozkural <eray@uludag.org.tr>

import bsddb3.db as db
import bsddb3.dbobj as dbobj
#import bsddb3.dbshelve as shelve
import pisi.dbshelve as shelve
import os
import fcntl
import types

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx
from pisi.util import join_path

from pisi.version import Version

class Error(pisi.Error):
    pass

def init_dbenv():
    if os.access(pisi.context.config.db_dir(), os.R_OK):
        # try to read version
        verfn = join_path(pisi.context.config.db_dir(), 'dbversion')
        if os.path.exists(verfn):
            verfile = file(verfn, 'r')
            ls = verfile.readlines()
            currver = Version(ls[0])
            dbver = Version(pisi.__dbversion__)
            if currver < dbver:
                raise Error(_('Database version insufficient. Please run rebuild-db command.'))
            elif currver > dbver:
                raise Error(_('Database version greater than PiSi version. You need a newer PiSi.'))
        else:
            if os.access(pisi.context.config.db_dir(), os.W_OK):
                ctx.ui.warning(_('Writing current database version'))
                verfile = file(verfn, 'w')
                verfile.write(pisi.__dbversion__)
                verfile.close()
            else:
                raise Error(_('Cannot attain write access to database environment'))
    else:
        raise Error(_('Cannot attain read access to database environment'))
    if os.access(pisi.context.config.db_dir(), os.W_OK):
        ctx.dbenv = dbobj.DBEnv()
        flags =  (db.DB_INIT_MPOOL |      # cache
                  db.DB_INIT_TXN |        # transaction subsystem
                  db.DB_INIT_LOG |        # logging subsystem
                  db.DB_RECOVER |         # run normal recovery
                  db.DB_CREATE)           # allow db to create files
        ctx.dbenv.open(pisi.context.config.db_dir(), flags)
        ctx.dbenv.set_flags(db.DB_LOG_AUTOREMOVE, 1) # clear inactive logs automatically
    else:
        ctx.ui.warning(_('Opening PİSİ database in read-only mode. Operations that require write access will fail.'))
        ctx.dbenv = None

#def open(filename, flags='r', mode = 0644, filetype = db.DB_BTREE):
#    db = LockedDBShelf(None, mode, filetype, None, True)
#    db.open(filename, filename, filetype, flags, mode)
#    return db

class LockedDBShelf(shelve.DBShelf):
    """A simple wrapper to implement locking for bsddb's dbshelf"""

    def __init__(self, dbname, mode=0644,
                 filetype=db.DB_BTREE, dbenv = None):
        if dbenv == None:
            dbenv = ctx.dbenv
        shelve.DBShelf.__init__(self, dbenv)
        filename = join_path(pisi.context.config.db_dir(), dbname + '.bdb')
        if os.access(os.path.dirname(filename), os.W_OK):
            flags = 'w'
            if not self.dbenv:
                raise Error(_('Database writes not allowed without transactions'))
        elif os.access(filename, os.R_OK):
            flags = 'r'
        else:
            raise Error(_('Cannot attain read or write access to database %s') % dbname)
        self.open(filename, dbname, filetype, flags, mode)

    def __del__(self):
        # superclass does something funky, we don't need that
        pass

    def open(self, filename, dbname, filetype, flags=db.DB_CREATE, mode=0644):
        self.filename = filename        
        self.closed = False
        if type(flags) == type(''):
            sflag = flags
            if sflag == 'r':
                flags = db.DB_RDONLY
            elif sflag == 'rw':
                flags = 0
            elif sflag == 'w':
                flags =  db.DB_CREATE
            elif sflag == 'c':
                flags =  db.DB_CREATE
            elif sflag == 'n':
                flags = db.DB_TRUNCATE | db.DB_CREATE
            else:
                raise Error, _("Flags should be one of 'r', 'w', 'c' or 'n' or use the bsddb.db.DB_* flags")
        self.flags = flags
        if self.flags & db.DB_RDONLY == 0:
            flags |= db.DB_AUTO_COMMIT # use txn subsystem in write mode
            self.lock()
        filename = os.path.realpath(filename) # we give absolute path due to dbenv
        #print 'opening', filename, filetype, flags, mode
        return self.db.open(filename, None, filetype, flags, mode)

    def lock(self):
        self.lockfile = file(self.filename + '.lock', 'w')
        try:
            fcntl.flock(self.lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            raise Error(_("Another instance of PISI is running. Only one instance is allowed to modify the PISI database at a time."))

    def close(self):
        if self.closed:
            return
        self.db.close()
        if self.flags & db.DB_RDONLY == 0:
            self.unlock()
        self.closed = True

    def unlock(self):
        self.lockfile.close()
        os.unlink(self.filename + '.lock')

    @staticmethod
    def encodekey(key):
        '''utility method for dbs that must store unicodes in keys'''
        if type(key)==types.UnicodeType:
            return key.encode('utf-8')
        elif type(key)==types.StringType:
            return key
        else:
            raise Error('Key must be either string or unicode')
