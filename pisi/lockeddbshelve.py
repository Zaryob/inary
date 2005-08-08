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
# A simple wrapper to implement locking for bsddb's dbshelf

# Authors:  Eray Ozkural <eray@uludag.org.tr>


import bsddb.dbshelve as shelve
import bsddb.db as db
import fcntl

def open(filename, flags=db.DB_CREATE, mode=0660, filetype=db.DB_HASH,
         dbenv=None, dbname=None):
    """
    A simple factory function for compatibility with the standard
    shleve.py module.  It can be used like this, where key is a string
    and data is a pickleable object:

        from bsddb import dbshelve
        db = dbshelve.open(filename)

        db[key] = data

        db.close()
    """
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
            raise error, "flags should be one of 'r', 'w', 'c' or 'n' or use the bsddb.db.DB_* flags"

    d = LockedDBShelf(dbenv)
    d.open(filename, dbname, filetype, flags, mode)
    return d

class LockedDBShelf(shelve.DBShelf):

    def __init__(self, env = None):
        shelve.DBShelf.__init__(self, env)

    def open(self, filename, dbname, filetype, flags, mode):
        self.lockfile = file(filename + '.lock', 'w')
        try:
            fcntl.flock(self.lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            import sys
            from ui import ui
            ui.error("Another instance of PISI is running. Try later!\n")
            sys.exit(1)
        return self.db.open(filename, dbname, filetype, flags, mode)

    def close(self):
        self.db.close()
        self.lockfile.close()

