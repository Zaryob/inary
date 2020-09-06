# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2020, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

"""misc. utility functions, including process and file utils"""

# Inary Modules
from inary.util.filesystem_terminal import get_terminal_size
import operator
from inary.util.filesystem_terminal import *
from functools import reduce
import inary
import inary.errors
import inary.context as ctx

# Gettext Library
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
punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
printable = digits + ascii_letters + punctuation + whitespace


def every(pred, seq):
    return reduce(operator.and_, list(map(pred, seq)), True)


def any(pred, seq):
    return reduce(operator.or_, list(map(pred, seq)), False)


def unzip(seq):
    return list(zip(*seq))


def concat(l):
    """Concatenate a list of lists."""
    return reduce(operator.concat, l)


def multisplit(str, chars):
    """Split str with any of the chars."""
    l = [str]
    for c in chars:
        l = concat([x.split(c) for x in l])
    return l


def same(l):
    """Check if all elements of a sequence are equal."""
    if len(l) == 0:
        return True
    else:
        last = l.pop()
        for x in l:
            if x != last:
                return False
        return True


def flatten_list(l):
    """Flatten a list of lists."""
    # Fastest solution is list comprehension
    # See:
    # http://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
    return [item for sublist in l for item in sublist]


def unique_list(l):
    """Creates a unique list by deleting duplicate items"""
    list_set = set(l)
    unique_list = (list(list_set))
    return [x for x in unique_list]


def strlist(l):
    """Concatenate string reps of l's elements."""
    return "".join([str(x) + ' ' for x in l])


def prefix(a, b):
    """Check if sequence a is a prefix of sequence b."""
    if len(a) > len(b):
        return False
    for i in range(0, len(a)):
        if a[i] != b[i]:
            return False
    return True


def remove_prefix(a, b):
    """Remove prefix a from sequence b."""
    assert prefix(a, b)
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


def human_readable_size(size=0):
    symbols, depth = [' B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'], 0

    while size > 1000 and depth < 8:
        size = float(size / 1024)
        depth += 1

    return size, symbols[depth]


def human_readable_rate(size=0):
    x = human_readable_size(size)
    return x[0], x[1] + '/s'


def format_by_columns(strings, sep_width=2):
    longest_str_len = len(max(strings, key=len))
    term_columns = get_terminal_size()[1]

    def get_columns(max_count):
        if longest_str_len > term_columns:
            return [longest_str_len]

        columns = []
        for name in strings:
            table_width = sum(columns) + len(name) + len(columns) * sep_width
            if table_width > term_columns:
                break

            columns.append(len(name))
            if len(columns) == max_count:
                break

        return columns

    def check_size(columns):
        total_sep_width = (len(columns) - 1) * sep_width

        for n, name in enumerate(strings):
            col = n % len(columns)
            if len(name) > columns[col]:
                columns[col] = len(name)

            if len(columns) > 1:
                width = sum(columns) + total_sep_width
                if width > term_columns:
                    return False

        return True

    columns = get_columns(term_columns)

    while not check_size(columns):
        columns = get_columns(len(columns) - 1)

    sep = " " * sep_width
    lines = []
    current_line = []
    for n, name in enumerate(strings):
        col = n % len(columns)
        current_line.append(name.ljust(columns[col]))

        if col == len(columns) - 1:
            lines.append(sep.join(current_line))
            current_line = []

    if current_line:
        lines.append(sep.join(current_line))

    return "\n".join(lines)
