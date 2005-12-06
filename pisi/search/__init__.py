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
# Author:  Eray Ozkural <eray@uludag.org.tr>

import pisi

class Error(pisi.Error):
    pass

class Exception(pisi.Exception):
    pass

# API    

from invertedindex import InvertedIndex

def init(ids, langs):
    "initialize databases"
    import pisi.context as ctx
    
    ctx.invidx = {}
    for id in ids:
        ctx.invidx[id] = {}
        for lang in langs:
            ctx.invidx[id][lang] = InvertedIndex(id, lang)

def finalize():
    import pisi.context as ctx
    
    for id in ctx.invidx.iterkeys():
        for lang in ctx.invidx[id].iterkeys():
            ctx.invidx[id][lang].close()
    
    ctx.invidx = {}    
    
def add_doc(id, lang, docid, str):
    pass

def remove_doc(id, lang, docid, str):
    pass

def query_terms(id, lang, terms):
    pass
