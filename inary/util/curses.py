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
import sys
import inary
import inary.errors
import inary.context as ctx

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


#############################
#   ncurses like functions  #
#############################


def initscr():
    """Clear and create a window"""
    printw("\x1b[s\x1bc")


def endwin():
    """Clear and restore screen"""
    printw("\x1bc\x1b[u")


def move(x, y):
    """Move"""
    printw("\x1b[{};{}f".format(y, x))


def printw(msg=''):
    """Print clone"""
    sys.stdout.write(msg)
    sys.stdout.flush()


def mvprintw(x, y, msg=''):
    """Move and print"""
    move(x, y)
    printw(msg)


def noecho(enabled=True):
    if not ctx.get_option('no_color'):
        if(enabled):
            printw("\x1b[?25l")
        else:
            printw("\x1b[?25h")


def attron(attribute):
    """Attribute enable"""
    if(attribute == "A_NORMAL"):
        sys.stdout.write("\x1b[;0m")
    elif(attribute == "A_UNDERLINE"):
        sys.stdout.write("\x1b[4m")
    elif(attribute == "A_REVERSE"):
        sys.stdout.write("\x1b[7m")
    elif(attribute == "A_BLINK"):
        sys.stdout.write("\x1b[5m")
    elif(attribute == "A_DIM"):
        sys.stdout.write("\x1b[2m")
    elif(attribute == "A_BOLD"):
        sys.stdout.write("\x1b[1m")
    elif(attribute == "A_INVIS"):
        sys.stdout.write("\x1b[8m")
    elif(attribute == "C_BLACK"):
        sys.stdout.write("\x1b[30m")
    elif(attribute == "C_RED"):
        sys.stdout.write("\x1b[31m")
    elif(attribute == "C_GREEN"):
        sys.stdout.write("\x1b[32m")
    elif(attribute == "C_YELLOW"):
        sys.stdout.write("\x1b[33m")
    elif(attribute == "C_BLUE"):
        sys.stdout.write("\x1b[34m")
    elif(attribute == "C_MAGENTA"):
        sys.stdout.write("\x1b[35m")
    elif(attribute == "C_CYAN"):
        sys.stdout.write("\x1b[36m")
    elif(attribute == "C_WHITE"):
        sys.stdout.write("\x1b374m")
    elif(attribute == "B_BLACK"):
        sys.stdout.write("\x1b[40m")
    elif(attribute == "B_RED"):
        sys.stdout.write("\x1b[41m")
    elif(attribute == "B_GREEN"):
        sys.stdout.write("\x1b[42m")
    elif(attribute == "B_YELLOW"):
        sys.stdout.write("\x1b[43m")
    elif(attribute == "B_BLUE"):
        sys.stdout.write("\x1b[44m")
    elif(attribute == "B_MAGENTA"):
        sys.stdout.write("\x1b[45m")
    elif(attribute == "B_CYAN"):
        sys.stdout.write("\x1b[46m")
    elif(attribute == "B_WHITE"):
        sys.stdout.write("\x1b[47m")
    sys.stdout.flush()


def drawbox(x1, y1, x2, y2):
    """Draw box"""
    mvprintw(x1, y1, "╔")
    mvprintw(x1, y2, "╚")
    mvprintw(x2, y1, "╗")
    mvprintw(x2, y2, "╝")
    for i in range((x1 + 1), (x2 - 1)):
        mvprintw(i, y1, "═")
        mvprintw(i, y2, "═")
    for i in range((y1 + 1), (y2 - 1)):
        mvprintw(x1, i, "║")
        mvprintw(x2, i, "║")
