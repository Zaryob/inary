# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

usage_text1 = """%prog <command> [options] [arguments]

where <command> is one of:

"""

usage_text2 = """
Use \"%prog help <command>\" for help on a specific subcommand.

PISI Package Manager
"""

def commonopts(parser):
    p = parser
    p.add_option("-D", "--destdir", action="store")
    p.add_option("", "--yes-all", action="store_true",
                 default=False, help = "assume yes in all yes/no queries")
    p.add_option("-u", "--username", action="store")
    p.add_option("-p", "--password", action="store")
    p.add_option("-P", action="store_true", dest="getpass", default=False,
                 help="Get password from the command line")
    p.add_option("-v", "--verbose", action="store_true",
                 dest="verbose", default=False,
                 help="detailed output")
    p.add_option("-d", "--debug", action="store_true",
                 default=True, help="show debugging information")
    p.add_option("-n", "--dry-run", action="store_true", default=False,
                 help = "do not perform any action, just show what\
                 would be done")
    return p
