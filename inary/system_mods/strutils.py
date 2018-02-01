# -*- coding: utf-8 -*-
#
# Copyright (C) 2006-2010 TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

"""string/list/functional utility functions"""

import operator
from functools import reduce

def every(pred, seq):
    return reduce(operator.and_, list(map(pred, seq)), True)

def any(pred, seq):
    return reduce(operator.or_, list(map(pred, seq)), False)

def unzip(seq):
    return list(zip(*seq))

def concat(l):
    """Concatenate a list of lists."""
    return reduce( operator.concat, l )

def strlist(l):
    """Concatenate string reps of l's elements."""
    return "".join([str(x) + ' ' for x in l])

def multisplit(str, chars):
    """Split str with any of the chars."""
    l = [str]
    for c in chars:
        l = concat([x.split(c) for x in l])
    return l

def same(l):
    """Check if all elements of a sequence are equal."""
    if len(l)==0:
        return True
    else:
        last = l.pop()
        for x in l:
            if x!=last:
                return False
        return True

def prefix(a, b):
    """Check if sequence a is a prefix of sequence b."""
    if len(a)>len(b):
        return False
    for i in range(0,len(a)):
        if a[i]!=b[i]:
            return False
    return True

def remove_prefix(a,b):
    """Remove prefix a from sequence b."""
    assert prefix(a,b)
    return b[len(a):]

def human_readable_size(size = 0):
    symbols, depth = [' B', 'KB', 'MB', 'GB'], 0

    while size > 1000 and depth < 3:
        size = float(size / 1024)
        depth += 1

    return size, symbols[depth]

def human_readable_rate(size = 0):
    x = human_readable_size(size)
    return x[0], x[1] + '/s'

def ascii_lower(str):
    """Ascii only version of string.lower()"""
    trans_table = str.maketrans(str.ascii_uppercase, str.ascii_lowercase)
    return str.translate(trans_table)

def ascii_upper(str):
    """Ascii only version of string.upper()"""
    trans_table = str.maketrans(str.ascii_lowercase, str.ascii_uppercase)
    return str.translate(trans_table)
