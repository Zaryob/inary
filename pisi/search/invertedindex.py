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
# Author:  Eray Ozkural <eray@uludag.org.tr>

import types

import pisi.lockeddbshelve as shelve

class InvertedIndex(object):
    """a database of term -> set of documents"""
    
    def __init__(self, id, lang):
        self.d = shelve.LockedDBShelf('ii-%s-%s' % (id, lang))

    def close(self):
        self.d.close()

    def has_term(self, term, txn = None):
        return self.d.has_key(shelve.LockedDBShelf.encodekey(term), txn)

    def get_term(self, term, txn = None):
        """get set of doc ids given term"""
        term = shelve.LockedDBShelf.encodekey(term)
        def proc(txn):
            if not self.has_term(term, txn):
                self.d.put(term, set(), txn)
            return self.d.get(term, txn)
        return self.d.txn_proc(proc, txn)

    def query(self, terms, txn = None):
        def proc(txn):
            docs = [ self.get_term(x, txn) for x in terms ]
            return reduce(lambda x,y: x.intersection(y), docs)
        return self.d.txn_proc(proc, txn)

    def list_terms(self, txn= None):
        list = []
        def f(txn):
            for term in self.d.iterkeys(txn):
                list.append(term)
            return list
        return self.d.txn_proc(f, txn)

    def add_doc(self, doc, terms, txn = None):
        def f(txn):
            for term_i in terms:
                term_i = shelve.LockedDBShelf.encodekey(term_i)
                term_i_docs = self.get_term(term_i, txn)
                term_i_docs.add(doc)
                self.d.put(term_i, term_i_docs, txn) # update
        return self.d.txn_proc(f, txn)

    def remove_doc(self, doc, terms):
        def f(txn):
            for term_i in terms:
                term_i = shelve.LockedDBShelf.encodekey(term_i)            
                term_i_docs = self.get_term(term_i)
                term_i_docs.remove(doc)
                self.d.put(term_i, term_i_docs, txn) # update
        return self.d.txn_proc(f, txn)
