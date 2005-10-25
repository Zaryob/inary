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

import bsddb.dbshelve as shelve
import bsddb.db as db
import os
import fcntl

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context

class Error(pisi.Error):
    pass

class LockedDBShelf(shelve.DBShelf):
    """A simple wrapper to implement locking for bsddb's dbshelf"""

    def __init__(self, dbname, mode=0644,
                 filetype=db.DB_HASH, dbenv=None):
        shelve.DBShelf.__init__(self, dbenv)
        filename = os.path.join( pisi.context.config.db_dir(), dbname + '.bdb')
        if os.access(os.path.dirname(filename), os.W_OK):
            flags = 'w'
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
        #print 'open', filename
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
        pisi.util.check_dir(pisi.context.config.db_dir())
        if self.flags != db.DB_RDONLY:
            self.lock()
        return self.db.open(filename, dbname, filetype, flags, mode)

    def lock(self):
        self.lockfile = file(self.filename + '.lock', 'w')
        try:
            fcntl.flock(self.lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            raise Error(_("Another instance of PISI is running. Try later!"))


    def close(self):
        if self.closed:
            return
        self.db.close()
        if self.flags != db.DB_RDONLY:
            self.unlock()
        self.closed = True

    def unlock(self):
        self.lockfile.close()
        os.unlink(self.filename + '.lock')
