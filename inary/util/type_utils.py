# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
# This module is part of  inary.util

from .term_utils import get_terminal_size
from functools import reduce
import unicodedata
import operator
import sys

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

#########################
# string/list/functional#
#########################

whitespace = ' \t\n\r\v\f'
ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
ascii_letters = ascii_lowercase + ascii_uppercase
digits = '0123456789'
hexdigits = digits + 'abcdef' + 'ABCDEF'
octdigits = '01234567'
punctuation = """!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
printable = digits + ascii_letters + punctuation + whitespace

def every(pred, seq):
    return reduce(operator.and_, list(map(pred, seq)), True)

def any(pred, seq):
    return reduce(operator.or_, list(map(pred, seq)), False)

def unzip(seq):
    return list(zip(*seq))

def concat(l):
    """Concatenate a list of lists."""
    return reduce( operator.concat, l )

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

def any(pred, seq):
    return reduce(operator.or_, list(map(pred, seq)), False)

def flatten_list(l):
    """Flatten a list of lists."""
    # Fastest solution is list comprehension
    # See: http://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
    return [item for sublist in l for item in sublist]

def strlist(l):
    """Concatenate string reps of l's elements."""
    return "".join([str(x) + ' ' for x in l])


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

def suffix(a, b):
    """Check if sequence a is a suffix of sequence b."""
    if len(a) > len(b):
        return False
    for i in range(1, len(a) + 1):
        if a[-i] != b[-i]:
            return False
    return True

def remove_suffix(a, b):
    """Remove suffix a from sequence b."""
    assert suffix(a, b)
    return b[:-len(a)]

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

# Python regex sucks
# http://mail.python.org/pipermail/python-list/2009-January/523704.html
def letters():
    start = end = None
    result = []
    for index in range(sys.maxunicode + 1):
        c = chr(index)
        if unicodedata.category(c)[0] == 'L':
            if start is None:
                start = end = c
            else:
                end = c
        elif start:
            if start == end:
                result.append(start)
            else:
                result.append(start + "-" + end)
            start = None
    return ''.join(result)
