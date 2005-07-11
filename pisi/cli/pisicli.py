# -*- coding: utf-8 -*-

import sys
from optparse import OptionParser

import pisi
from pisi.cli import buildhelper, installhelper, indexhelper
from pisi.config import config

usage = """%prog <command> [options] [arguments]

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

class ParserError:
    def __init__(self, msg):
        self.msg = msg

class Parser(OptionParser):

    def __init__(self, usage, version):
        OptionParser.__init__(self, usage=usage, version=version)

    def error(self, msg):
        raise ParserError(msg)

# eheh, burada ne yaptigim anlasilamamis galiba
# sunlari yazin:
# pisi-cli --test remove x
# pisi-cli --test build x
# diger turlu olmaz bu. dikkat. per command optionlar
# svn log'unda anlatmistim. simdi bir daha yazmam gerekti bazi
# seyleri bastan calistirabilmek icin. bir ise yaramasa yapmazdim.

class PisiCLI(object):

    commands = ["help", "build", "info", "install",
                "remove", "index", "updatedb"]
    
    def commonopts(self):
        p = self.parser
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


    def __init__(self):
        # first construct a parser for common options
        # this is really dummy
        self.parser = Parser(usage=usage, version="%prog " + pisi.__version__)
        #self.parser.allow_interspersed_args = False
        self.commonopts()

        self.command = ""
        try:
            (options, args) = self.parser.parse_args()
            #if len(parser.rargs)==0:
            #    self.die()
            self.command = args[0]
        except ParserError:
            # fully expected :) let's see if we got an argument
            if len(self.parser.rargs)==0:
                self.die()
            self.command = self.parser.rargs[0]

        #print '*', self.command

        # now for the real parser THIS IS ABSOLUTELY NECESSARY
        self.parser = OptionParser(usage=usage,
                                   version="%prog " + pisi.__version__)
        #self.parser.allow_interspersed_args = False
        self.commonopts()    
        self.add_subcommand_opts()
        (self.options, args) = self.parser.parse_args()
        self.args = args[1:]

        self.authInfo = None
        self.checkAuthInfo()

    def die(self):
        print usage
        sys.exit(1)

    def add_subcommand_opts(self):
        if self.command in self.commands:
            f = self.__getattribute__(self.command + '_opts')
            f()
        else:
            print 'Unrecognized command:', self.command
            self.die()

    def runCommand(self):
        if self.command in self.commands:
            f = self.__getattribute__(self.command)
            f()
        else:
            print 'Unrecognized command:', self.command
            self.die()

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
        return
            

    # FIX: her komut için ayrı help

    help_help = """help: display help
usage: help
help <command>"""
    
    def help_opts(self):
        pass

    def help(self, command=""):
        if not self.args:
            print usage
            return

        if command !="":
            print self.__getattribute__(command + '_help')
        else:
            print self.__getattribute__(self.args[0] + '_help')

    info_help = """info: display information about a package 
usage: info <package> ...
"""
    def info_opts(self):
        pass

    def info(self):
        if not self.args:
            self.help("info")
        for arg in self.args:
            self.printinfo(arg)

    def printinfo(self, arg):
        import os.path
        if os.path.exists(arg):
            metadata, files = pisi.install.get_pkg_info(arg)
            print metadata.package

    index_help = """index: Index PISI files in a given directory"""

    def index_opts(self):
        pass

    def index(self):
        if not self.args:
            self.help("index")

        if len(self.args)==1:
            indexhelper.index(self.args[0])
        elif len(self.args)==0:
            indexhelper.index()
        else:
            print 'Indexing only a single directory supported'
            self.die()

    install_help = """install: install PISI packages"""

    def install_opts(self):
        self.parser.add_option("", "--test", action="store_true",
                               default=True, help="xxxx")

    def install(self):
        if not self.args:
            self.help("install")
        for arg in self.args:
            installhelper.install(arg)

    build_help = """build: compile PISI packages"""

    def build_opts(self):
        pass

    def build(self):
        if not self.args:
            self.help("build")

        for arg in self.args:
            buildhelper.build(arg, self.authInfo)

    remove_help = """remove: remove PISI packages"""

    def remove_opts(self):
        self.parser.add_option("", "--test", action="store_true",
                               default=True, help="xxxx")

    def remove(self):
        if not self.args:
            self.help("install")
        for arg in self.args:
            pisi.install.remove(arg)

    updatedb_help = """updatedb: update source and package databases"""

    def updatedb_opts(self):
        pass

    def updatedb(self):
        """Update the repos db with the given index file (pisi-index.xml)"""
        if len(self.args) != 1:
            self.help("updatedb")

        indexfile = self.args[0]
        indexhelper.updatedb(indexfile)
