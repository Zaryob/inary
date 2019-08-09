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

import inary.context as ctx

import os
import sys
import fcntl
import struct
import termios

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

######################
# Terminal functions #
######################

def get_terminal_size():
    try:
        ret = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, "1234")
    except IOError:
        rows = int(os.environ.get("LINES", 25))
        cols = int(os.environ.get("COLUMNS", 80))
        return rows, cols

    return struct.unpack("hh", ret)

def xterm_title(message):
    """Set message as console window title."""
    if "TERM" in os.environ and sys.stderr.isatty():
        terminalType = os.environ["TERM"]
        for term in ["xterm", "Eterm", "aterm", "rxvt", "screen", "kterm", "rxvt-unicode"]:
            if terminalType.startswith(term):
                sys.stderr.write("\x1b]2;"+str(message)+"\x07")
                sys.stderr.flush()
                break

def xterm_title_reset():
    """Reset console window title."""
    if "TERM" in os.environ:
        xterm_title("")

def colorize(msg, color):
    """Colorize the given message for console output"""
    if color in ctx.const.colors and not ctx.get_option('no_color'):
        return str(ctx.const.colors[color] + msg + ctx.const.colors['default'])
    else:
        return str(msg)

def format_by_columns(strings, sep_width=2):
    longest_str_len = len(max(strings, key=len))
    term_rows, term_columns = get_terminal_size()

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
