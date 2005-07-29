usage_text = """%prog <command> [options] [arguments]

where <command> is one of:

help
build
build-unpack
build-runsetupaction
build-runbuildaction
build-runinstallaction
index
info
install
list-installed
list-available
remove
add-repo
remove-repo
list-repo
update-repo

Use \"%prog help <command>\" for help on a specific subcommand.

PISI Package Manager
"""

def commonopts(parser):
    p = parser
    p.add_option("-D", "--destdir", action="store")
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
