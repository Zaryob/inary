from optparse import OptionParser

def add(parser):

    parser.add_option("-D", "--destdir", action="store")
    parser.add_option("-v", "--verbose", action="store_true",
                      dest="verbose", default=False,
                      help="detailed output")
    parser.add_option("-d", "--debug", action="store_true", default=True)
    parser.add_option("-n", "--dry-run", action="store_true", default=False,
                      help = "do not perform any action, just show what\
                      would be done")
    return parser

