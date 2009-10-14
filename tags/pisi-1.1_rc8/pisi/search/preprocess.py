# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import tokenize
import locale

def normalize(lang, terms):
    if lang == "tr":
        old_locale = locale.setlocale(locale.LC_CTYPE)
        locale.setlocale(locale.LC_CTYPE, "tr_TR.UTF-8")
    terms = map(lambda x: unicode(x).lower(), terms)
    if lang == "tr":
        locale.setlocale(locale.LC_CTYPE, old_locale)
    unique_terms = set()
    for term in terms:
        unique_terms.add(unicode(term))
    return list(unique_terms)

def preprocess(lang, str):
    terms = tokenize.tokenize(lang, str)
    return normalize(lang, terms)
