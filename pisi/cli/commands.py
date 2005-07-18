import sys
from optparse import OptionParser
import pisi
from pisi.config import config
from pisi.purl import PUrl
from common import *

# helper functions
def cmdObject(cmd, fail=False):
    commands = {"help": Help,
                "build": Build,
                "info": Info,
                "install": Install,
                "remove": Remove,
                "index": Index,
                "updatedb": UpdateDB}

    if commands.has_key(cmd):
        obj = commands[cmd]()
        return obj

    if fail:
        print "Unrecognized command: ", cmd
        sys.exit(1)
    else:
        return None

class Command(object):
    """generic help string for any command"""
    def __init__(self):
        # now for the real parser
        self.parser = OptionParser(usage="",
                                   version="%prog " + pisi.__version__)
        self.options()
        self.parser = commonopts(self.parser)
        (self.options, args) = self.parser.parse_args()
        self.args = args[1:]

        self.checkAuthInfo()

    def options(self):
        """This is a fall back function. If the implementer module provides an
        options function it will be called"""
        pass

    def checkAuthInfo(self):
        username = self.options.username
        password = self.options.password

        # TODO: We'll get the username, password pair from a configuration
        # file from users home directory. Currently we need user to
        # give it from the user interface.
#         if not username and not password:
#             if someauthconfig.username and someauthconfig.password:
#                 self.authInfo = (someauthconfig.username,
#                                  someauthconfig.password)
#                 return
        if username and password:
            self.authInfo = (username, password)
            return
        
        if username and self.options.getpass:
            from getpass import getpass
            password = getpass("Password: ")
            self.authInfo = (username, password)
        else:
            self.authInfo = None

    def help(self):
        print getattr(self, "__doc__")

class Help(Command):
    """prints usage"""
    def __init__(self):
        super(Help, self).__init__()

    def run(self):
        if not self.args:
            print usage_text
            print self.parser.format_option_help()
            return
        
        for arg in self.args:
            obj = cmdObject(arg, True)
            obj.help()
#            print "\n",self.parser.format_option_help()
                
class Build(Command):
    """build: compile PISI package using a pspec.xml file"""
    def __init__(self):
        super(Build, self).__init__()

    def run(self):
        if not self.args:
            self.help()
            return

        from pisi.cli import buildhelper
        for arg in self.args:
            buildhelper.build(arg, self.authInfo)

class Install(Command):
    """install: install PISI packages"""
    def __init__(self):
        super(Install, self).__init__()

    def options(self):
        self.parser.add_option("", "--test", action="store_true",
                               default=True, help="xxxx")

    def run(self):
        if not self.args:
            self.help()
            return

        from pisi.operations import install
        for arg in self.args:
            install(arg)

class Remove(Command):
    """remove: remove PISI packages"""
    def __init__(self):
        super(Remove, self).__init__()

    def options(self):
        self.parser.add_option("", "--test", action="store_true",
                               default=True, help="xxxx")

    def run(self):
        if not self.args:
            self.help()
            return

        from pisi.operations import remove
        for arg in self.args:
            remove(arg)

class Info(Command):
    """info: display information about a package 
    usage: info <package> ..."""
    def __init__(self):
        super(Info, self).__init__()

    def run(self):
        if not self.args:
            self.help()
            return

        for arg in self.args:
            self.printinfo(arg)

    def printinfo(self, arg):
        import os.path
        from pisi.operations import info

        if os.path.exists(arg):
            metadata, files = info(arg)
            print metadata.package

class Index(Command):
    """index: Index PISI files in a given directory"""
    def __init__(self):
        super(Index, self).__init__()

    def run(self):
        if not self.args:
            self.help()
            return

        from pisi.cli import indexhelper
        if len(self.args)==1:
            indexhelper.index(self.args[0])
        elif len(self.args)==0:
            indexhelper.index()
        else:
            print 'Indexing only a single directory supported'
            return

class UpdateDB(Command):
    """updatedb: update source and package databases"""
    def __init__(self):
        super(UpdateDB, self).__init__()

    def run(self):
        if len(self.args) != 1:
            self.help()
            return

        from pisi.cli import indexhelper
        indexfile = self.args[0]
        indexhelper.updatedb(indexfile)


