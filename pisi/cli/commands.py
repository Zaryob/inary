# -*- coding:utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import sys
from optparse import OptionParser

import pisi
from pisi.uri import URI


def commands_string():
    s = ''
    list = commands.keys()
    list.sort()
    for x in list:
        s += x + '\n'
    return s


def get_command(cmd, fail=False):

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
        import pisi
        self.parser = OptionParser(usage=getattr(self, "__doc__"),
                                   version="%prog " + pisi.__version__)
        self.options()
        self.commonopts()
        (self.options, self.args) = self.parser.parse_args()
        self.args.pop(0)                # exclude command arg

        import pisi

        # initialize PiSi
        pisi.config.config = pisi.config.Config(self.options)
        pisi.ui.ui = pisi.ui.CLI(self.options.debug)
        
        self.check_auth_info()

    def commonopts(self):
        '''common options'''
        p = self.parser
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

    def options(self):
        """This is a fall back function. If the implementer module provides an
        options function it will be called"""
        pass

    def check_auth_info(self):
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

    def init(self, database = False):
        """initialize PiSi components"""
        
        # NB: command imports here or in the command class run fxns
        import pisi.toplevel
        from pisi.ui import ui

        # initialize repository databases
        if database:
            from pisi.repodb import repodb
            repodb.init_dbs()

    def finalize(self):
        """do cleanup work for PiSi components"""
        pass
        
    def name(self):
        """(command name, shortname) pair to be filled by subclasses"""
        pass

    def format_name(self):
        (name, shortname) = self.name()
        if shortname:
            return "%s (%s)" % (name, shortname)
        else:
            return name

    def help(self):
        """print help for the command"""
        pisi.ui.ui.info(self.format_name() + ': ')
        print getattr(self, "__doc__")
        print self.parser.format_option_help()

    def die(self):
        """exit program"""
        print 'Program terminated abnormally.'
        sys.exit(-1)


class Help(Command):
    """Prints help for given commands.

Usage: help [ <command1> <command2> ... <commandn> ]

If run without parameters, it prints the general help."""

    def __init__(self):
        #TODO? Discard Help's own usage doc in favor of general usage doc
        #self.__doc__ = usage_text
        #self.__doc__ += commands_string()
        super(Help, self).__init__()

    def name(self):
        return ("help", "h")

    def run(self):
        if not self.args:
            self.parser.set_usage(usage_text)
            self.parser.print_help()
            return
            
        self.init()
        
        for arg in self.args:
            obj = get_command(arg, True)
            obj.help()
            print
        
        self.finalize()

        
def buildno_opts(self):
    self.parser.add_option("", "--ignore-build-no", action="store_true",
                           default=False,
                           help="Don't take build no into account.")        


class Build(Command):
    """Build a PISI package using a pspec.xml file

Usage: build <pspec.xml>

You can give a URI of the pspec.xml file. PISI will
fetch all necessary files and build the package for you.
"""
    def __init__(self):
        super(Build, self).__init__()

    def name(self):
        return ("build", "bi")

    def options(self):
        buildno_opts(self)
        self.parser.add_option("-O", "--output-dir", action="store", default=".",
                               help="output directory for produced packages")       

    def run(self):
        if not self.args:
            self.help()
            return

        self.init()
        from pisi.config import config
        pisi.ui.ui.info('Output directory: %s\n' % config.options.output_dir)
        for arg in self.args:
            pisi.toplevel.build(arg, self.authInfo)
        self.finalize()


class PackageOp(Command):
    """Abstract package operation command"""
    def __init__(self):
        super(PackageOp, self).__init__()

    def options(self):
        self.parser.add_option("", "--ignore-comar", action="store_true",
                               default=False, help="xxxx")
##        self.parser.add_option("", "--ignore-dependency",
##                               action="store_true",
##                               default=False, help="xxxx")

    def init(self):
        super(PackageOp, self).init(True)
        import pisi
        import pisi.comariface
        if not self.options.ignore_comar:
            try:
                pisi.comariface.init()
            except pisi.comariface.ComarError:
                pisi.ui.ui.error('Comar error encountered\n')
                self.die()
                
    def finalize(self):
        #self.finalize_db()
        if not self.options.ignore_comar:
            pass
            #try:
            #    pisi.comariface.finalize()
            #except pisi.comariface.ComarError:
            #    ui.error('Comar error encountered\n')

        
class Install(PackageOp):
    """Install PISI packages

Usage: install <package1> <package2> ... <packagen>

You may use filenames, URIs or package names for packages. If you have
specified a package name, it should exist in a specified repository.
"""
    def __init__(self):
        super(Install, self).__init__()

    def name(self):
        return ("install", "it")

    def options(self):
        super(Install, self).options()
        buildno_opts(self)

    def run(self):
        if not self.args:
            self.help()
            return

        self.init()
        pisi.toplevel.install(self.args)
        self.finalize()


class Upgrade(PackageOp):
    """Upgrade PISI packages

Usage: Upgrade <package1> <package2> ... <packagen>

You may use filenames, URIs or package names for packages. If you have
specified a package name, it should exist in a specified repository.
"""
    def __init__(self):
        super(Upgrade, self).__init__()

    def name(self):
        return ("upgrade", "up")

    def options(self):
        super(Upgrade, self).options()
        buildno_opts(self)

    def run(self):
        if not self.args:
            self.help()
            return

        self.init()
        pisi.toplevel.upgrade(self.args)
        self.finalize()


class Remove(PackageOp):
    """Remove PISI packages

Usage: remove <package1> <package2> ... <packagen>

Remove package(s) from your system. Just give the package names to remove.
"""
    def __init__(self):
        super(Remove, self).__init__()

    def name(self):
        return ("remove", "rm")

    def run(self):
        if not self.args:
            self.help()
            return

        self.init()
        pisi.toplevel.remove(self.args)
        self.finalize()


class ConfigurePending(PackageOp):
    """configure pending packages
    """
    
    def __init__(self):
        super(ConfigurePending, self).__init__()

    def name(self):
        return ("configure-pending", "cp")

    def run(self):

        self.init()
        pisi.toplevel.configure_pending()
        self.finalize()


class Info(Command):
    """Display package information

Usage: info <package1> <package2> ... <packagen>

"""
    def __init__(self):
        super(Info, self).__init__()

    def name(self):
        return ("info", "i")

    def run(self):
        if not self.args:
            self.help()
            return

        self.init()
        for arg in self.args:
            self.printinfo(arg)
        self.finalize()

    def printinfo(self, arg):
        import os.path

        if os.path.exists(arg):
            metadata, files = pisi.toplevel.info(arg)
            print metadata.package


class Index(Command):
    """Index PISI files in a given directory

Usage: index <directory>

This command searches for all PiSi files in a directory, collects PiSi
tags from them and accumulates the information in an output XML file,
named by default 'pisi-index.xml'. In particular, it indexes both
source and binary packages.
"""
    def __init__(self):
        super(Index, self).__init__()

    def name(self):
        return ("index", "ix")

    def options(self):
        self.parser.add_option("-a", "--absolute-uris", action="store_true",
                               default=False,
                               help="store absolute links for indexed files.")

    def run(self):
        
        self.init()
        from pisi.toplevel import index
        if len(self.args)==1:
            index(self.args[0])
        elif len(self.args)==0:
            print 'Indexing current directory.'
            index()
        else:
            print 'Indexing only a single directory supported.'
            return
        self.finalize()


class ListInstalled(Command):
    """Print the list of all installed packages  

Usage: list-installed

"""

    def __init__(self):
        super(ListInstalled, self).__init__()

    def name(self):
        return ("list-installed", "li")

    def options(self):
        self.parser.add_option("-l", "--long", action="store_true",
                               default=False, help="show in long format")
        self.parser.add_option("-i", "--install-info", action="store_true",
                               default=False, help="show detailed install info")

    def run(self):
        self.init(True)
        from pisi.installdb import installdb
        list = installdb.list_installed()
        list.sort()
        if self.options.install_info:
            print 'Package Name     |St|   Version|  Rel.| Build|  Distro|             Date'
            print '========================================================================'
        for pkg in list:
            package = pisi.packagedb.inst_packagedb.get_package(pkg)
            inst_info = installdb.get_info(pkg)
            if self.options.long:
                print package
                print inst_info
            elif self.options.install_info:
                print '%-15s | %s ' % (package.name, inst_info.one_liner())
            else:
                print '%15s - %s ' % (package.name, package.summary)
        self.finalize()


class UpdateRepo(Command):
    """Update repository databases

Usage: update-repo <repo1> <repo2> ... <repon>

<repoi>: repository name
Synchronizes the PiSi databases with the current repository.
"""
    def __init__(self):
        super(UpdateRepo, self).__init__()

    def name(self):
        return ("update-repo", "ur")

    def run(self):
        if not self.args:
            self.help()
            return

        self.init(True)
        for repo in self.args:
            pisi.toplevel.update_repo(repo)
        self.finalize()


class AddRepo(Command):
    """Add a repository

Usage: add-repo <repo> <indexuri>

<repo>: name of repository to add
<indexuri>: URI of index file

NB: We support only local files (e.g., /a/b/c) and http:// URIs at the moment
"""
    def __init__(self):
        super(AddRepo, self).__init__()

    def name(self):
        return ("add-repo", "ar")

    def run(self):

        if len(self.args)>=2:
            self.init()
            name = self.args[0]
            indexuri = self.args[1]
            pisi.toplevel.add_repo(name, indexuri)
            self.init()
        else:
            self.help()
            return


class RemoveRepo(Command):
    """Remove repositories

Usage: remove-repo <repo1> <repo2> ... <repon>

Remove all repository information from the system.
"""
    def __init__(self):
        super(RemoveRepo, self).__init__()

    def name(self):
        return ("remove-repo", "rr")

    def run(self):

        if len(self.args)>=1:
            self.init()
            for repo in self.args:
                pisi.toplevel.remove_repo(repo)
            self.finalize()
        else:
            self.help()
            return


class ListRepo(Command):
    """List repositories

Usage: list-repo

Lists currently tracked repositories.
"""
    def __init__(self):
        super(ListRepo, self).__init__()

    def name(self):
        return ("list-repo", "lr")

    def run(self):

        self.init()
        from pisi.repodb import repodb
        for repo in repodb.list():
            print repo
            print '  ', repodb.get_repo(repo).indexuri.get_uri()
        self.finalize()


class ListAvailable(Command):
    """List available packages in the repositories

Usage: list-available [ <repo1> <repo2> ... repon ]

Gives a brief list of PiSi components published in the repository.
"""
    def __init__(self):
        super(ListAvailable, self).__init__()

    def name(self):
        return ("list-available", "li")

    def run(self):
        from pisi.repodb import repodb
        from pisi.ui import ui

        self.init(True)

        if self.args:
            for arg in self.args:
                self.print_packages(arg)
        else:
            # print for all repos
            for repo in repodb.list():
                ui.info("Repository : %s\n" % repo)
                self.print_packages(repo)
        self.finalize()

    def print_packages(self, repo):
        from pisi import packagedb

        pkg_db = packagedb.get_db(repo)
        list = pkg_db.list_packages()
        list.sort()
        for p in list:
            print p


class ListPending(Command):
    """List pending packages"""
    
    def __init__(self):
        super(ListPending, self).__init__()
    
    def name(self):
        return ("list-pending", "lp")

    def run(self):
        from pisi.installdb import installdb
        from pisi.ui import ui

        self.init(True)

        list = installdb.list_pending()
        list.sort()
        for p in list:
            print p

        self.finalize()


class SearchAvailable(Command):
    """Search in available packages

Usage: search-available <search pattern>

FIXME: this is bogus
"""
    pass


# Partial build commands        

class BuildUntil(Command):
    """Run the build process partially

Usage: -sStateName build-until <pspec file>

where states are:
unpack, setupaction, buildaction, installaction, buildpackages

You can give an URI of the pspec.xml file. PISI will fetch all
necessary files and unpack the source and prepare a source directory
for you.
"""
    def __init__(self):
        super(BuildUntil, self).__init__()

    def name(self):
        return ("build-until", "bu")

    def options(self):
        self.parser.add_option("-s", action="store", dest="state")

    def run(self):

        if not self.args:
            self.help()
            return

        self.init()
        state = self.options.state

        for arg in self.args:
            pisi.toplevel.build_until(arg, state, self.authInfo)
        self.finalize()


class BuildUnpack(Command):
    """Unpack the source archive

Usage: build-dounpack <pspec file>

TODO: desc.
"""
    def __init__(self):
        super(BuildUnpack, self).__init__()

    def name(self):
        return ("build-unpack", "biu")

    def run(self):
        if not self.args:
            self.help()
            return

        self.init()
        for arg in self.args:
            pisi.toplevel.build_until(arg, "unpack", self.authInfo)
        self.finalize()


class BuildSetup(Command):
    """Setup the source

Usage: build-dosetup <pspec file>

TODO: desc.
"""
    def __init__(self):
        super(BuildSetup, self).__init__()

    def name(self):
        return ("build-setup", "bis")

    def run(self):
        if not self.args:
            self.help()
            return

        self.init()
        for arg in self.args:
            pisi.toplevel.build_until(arg, "setupaction",
                                      self.authInfo)
        self.finalize()


class BuildBuild(Command):
    """Setup the source

Usage: build-dobuild <pspec file>

TODO: desc.
"""
    def __init__(self):
        super(BuildBuild, self).__init__()

    def name(self):
        return ("build-dobuild", "bib")

    def run(self):
        if not self.args:
            self.help()
            return

        self.init()
        for arg in self.args:
            pisi.toplevel.build_until(arg, "buildaction", self.authInfo)
        self.finalize()


class BuildInstall(Command):
    """Install to the sandbox

Usage: build-doinstall <pspec file>

TODO: desc.
"""
    def __init__(self):
        super(BuildInstall, self).__init__()

    def name(self):
        return ("build-doinstall", "bii")

    def run(self):
        if not self.args:
            self.help()
            return

        self.init()
        for arg in self.args:
            pisi.toplevel.build_until(arg, "installaction",
                                      self.authInfo)
        self.finalize()


class BuildPackage(Command):
    """Setup the source

Usage: build-dobuild <pspec file>

TODO: desc.
"""
    def __init__(self):
        super(BuildPackage, self).__init__()

    def name(self):
        return ("build-dopackage", "bip")

    def run(self):
        if not self.args:
            self.help()
            return

        self.init()
        for arg in self.args:
            pisi.toplevel.build_until(arg, "buildpackages", self.authInfo)
        self.finalize()

# command dictionary

commands = {"help": Help,
            "build": Build,
            "build-until": BuildUntil,
            "build-unpack": BuildUnpack,
            "build-setup": BuildSetup,
            "build-build": BuildBuild,
            "build-install": BuildInstall,
            "build-package": BuildPackage,
            "info": Info,
            "install": Install,
            "configure-pending": ConfigurePending,
            "list-pending": ListPending,
            "list-installed": ListInstalled,
            "list-available": ListAvailable,
            "search-available": SearchAvailable,
            "remove": Remove,
            "upgrade": Upgrade,
            "index": Index,
            "update-repo": UpdateRepo, 
            "add-repo": AddRepo, 
            "remove-repo": RemoveRepo, 
            "list-repo": ListRepo
            }

usage_text1 = """%prog <command> [options] [arguments]

where <command> is one of:

"""

usage_text2 = """
Use \"%prog help <command>\" for help on a specific command.
"""

usage_text = (usage_text1 + commands_string() + usage_text2)
