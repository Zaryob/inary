# -*- coding: utf-8 -*-

import sys
from optparse import OptionParser

import pisi
from pisi.config import config


# globals
usage_text = """%prog <command> [options] [arguments]

where <command> is one of:

help
build
index
info
install
remove
updatedb

Use \"%prog help <command>\" for help on a specific subcommand.

PISI Package Manager
"""

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


######## start commands #########
class Command(object):
    """generic help string for any command"""
    def __init__(self):
        # now for the real parser THIS IS ABSOLUTELY NECESSARY
        self.parser = OptionParser(usage=usage_text,
                                   version="%prog " + pisi.__version__)
        #self.parser.allow_interspersed_args = False
        self.options()
        self.parsr = commonopts(self.parser)
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
        if not username and not password:
            if config.username and config.password:
                self.authInfo = (config.username, config.password)
                return
        elif username and password:
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
            return
        
        for arg in self.args:
            obj = cmdObject(arg, True)
            obj.help()
                
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

        from pisi.cli import installhelper
        for arg in self.args:
            installhelper.install(arg)


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

        for arg in self.args:
            pisi.install.remove(arg)

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
        if os.path.exists(arg):
            metadata, files = pisi.install.get_pkg_info(arg)
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
######## end commands #########

class ParserError(Exception):
    pass

class Parser(OptionParser):
    def __init__(self, version):
        OptionParser.__init__(self, usage=usage_text, version=version)

    def error(self, msg):
        raise ParserError, msg

class PisiCLI(object):

    def __init__(self):
        # first construct a parser for common options
        # this is really dummy
        self.parser = Parser(version="%prog " + pisi.__version__)
        #self.parser.allow_interspersed_args = False
        self.parser = commonopts(self.parser)

        cmd = ""
        try:
            (options, args) = self.parser.parse_args()
            #if len(parser.rargs)==0:
            #    self.die()
            cmd = args[0]
        except IndexError:
            self.die()
        except ParserError:
            # fully expected :) let's see if we got an argument
            if len(self.parser.rargs)==0:
                self.die()
            cmd = self.parser.rargs[0]

        #print '*', cmd
        self.command = cmdObject(cmd)
        if not self.command:
            print "Unrecognized command: ", cmd
            self.die()

    def die(self):
        print usage_text
        sys.exit(1)

    def runCommand(self):
        self.command.run()
