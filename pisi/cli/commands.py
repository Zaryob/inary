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
from pisi.config import config
from pisi.purl import PUrl
from common import *
import pisi.toplevel
from pisi.ui import ui

# helper functions
def cmdObject(cmd, fail=False):
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
                "index": Index,
                "update-repo": UpdateRepo, 
                "add-repo": AddRepo, 
                "remove-repo": RemoveRepo, 
                "list-repo": ListRepo
                }

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
        self.parser = OptionParser(usage=usage_text,
                                   version="%prog " + pisi.__version__)
        self.options()
        self.parser = commonopts(self.parser)
        (self.options, args) = self.parser.parse_args()
        self.args = args[1:]

        # initialize PiSi
        pisi.config.config = pisi.config.Config(self.options)
        cli = pisi.ui.CLI(self.options.debug)
        pisi.ui.ui = cli
        
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

    def init_db(self):
        from pisi.repodb import repodb
        repodb.init_dbs()

    def help(self):
        print getattr(self, "__doc__")

    def die(self):
        print 'Program terminated abnormally.'
        sys.exit(-1)

class Help(Command):
    """Prints usage

    Usage:
    help [command-name]

If run without parameters will print the general usage documentation.

If run with a command name as the parameter will print the documentation
for that command.
"""
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
    """Build a PISI package using a pspec.xml file

    Usage:
    build pspec.xml

You can give an URI of the pspec.xml file. PISI will
fetch all necessary files and build the package for you.
"""
    def __init__(self):
        super(Build, self).__init__()

    def run(self):
        if not self.args:
            self.help()
            return

        for arg in self.args:
            pisi.toplevel.build(arg, self.authInfo)

class PackageOp(Command):
    """Abstract package operation command"""
    def __init__(self):
        super(PackageOp, self).__init__()

    def options(self):
        self.parser.add_option("", "--ignore-comar", action="store_true",
                               default=False, help="xxxx")
        self.parser.add_option("", "--ignore-dependency",
                               action="store_true",
                               default=False, help="xxxx")

    def init(self):
        self.init_db()
        import pisi.comariface
        if not self.options.ignore_comar:
            try:
                pisi.comariface.init()
            except pisi.comariface.ComarError:
                ui.error('Comar error encountered\n')
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

    Usage:
    install package

You can give an URI of the pisi package. Or you can just give a
package name and choose to install a package from the defined
repositories (with add-repo).
"""
    def __init__(self):
        super(Install, self).__init__()
        print pisi.config.config.options

    def run(self):
        if not self.args:
            self.help()
            return

        self.init()
        pisi.toplevel.install(self.args)
        self.finalize()

class Remove(PackageOp):
    """Remove PISI packages

    Usage:
    remove package-name

Remove a package from your system. Just give the package name to remove.
"""
    def __init__(self):
        super(Remove, self).__init__()

    def run(self):
        if not self.args:
            self.help()
            return

        self.init()
        pisi.toplevel.remove(self.args)
        self.finalize()

class ConfigurePending(PackageOp):
    """configure pending packages"""
    def __init__(self):
        super(Remove, self).__init__()

    def run(self):
        #if not self.args:
        #    self.help()
        #    return

        self.init()
        pisi.toplevel.configure_pending()
        self.finalize()

class Info(Command):
    """Display information about a package 

    Usage: 
    info <package>

TODO: Some description...
"""
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
            metadata, files = pisi.toplevel.info(arg)
            print metadata.package

class Index(Command):
    """Index PISI files in a given directory

    Usage:
    index directory

TODO: Some description...
"""
    def __init__(self):
        super(Index, self).__init__()

    def run(self):
        if not self.args:
            self.help()
            return

        from pisi.toplevel import index
        if len(self.args)==1:
            index(self.args[0])
        elif len(self.args)==0:
            index()
        else:
            print 'Indexing only a single directory supported'
            return

class ListInstalled(Command):
    """Print the list of all installed packages  

    Usage:
    list-installed

TODO: Some description...
"""

    def __init__(self):
        super(ListInstalled, self).__init__()

    def options(self):
        self.parser.add_option("-l", "--long", action="store_true",
                               default=False, help="show in long format")

    def run(self):
        self.init_db()
        from pisi.installdb import installdb
        for pkg in installdb.list_installed():
            package = pisi.packagedb.get_package(pkg)
            if not self.options.long:
                print package.name, '-', package.summary
            else:
                print package

class UpdateRepo(Command):
    """Update the databases of a repository

    Usage:
    update-repo <repo1> <repo2>

TODO: Some description...
"""
    def __init__(self):
        super(UpdateRepo, self).__init__()

    def run(self):
        if not self.args:
            self.help()
            return

        self.init_db()
        for repo in self.args:
            pisi.toplevel.update_repo(repo)

class AddRepo(Command):
    """Add a repository

    Usage:
    add-repo <repo> <indexuri>

TODO: Some description...
"""
    def __init__(self):
        super(AddRepo, self).__init__()

    def run(self):

        if len(self.args)>=2:
            name = self.args[0]
            indexuri = self.args[1]
            pisi.toplevel.add_repo(name, indexuri)
        else:
            self.help()
            return

class RemoveRepo(Command):
    """Remove a repository

    Usage:
    remove-repo <repo>

TODO: Some description...
"""
    def __init__(self):
        super(RemoveRepo, self).__init__()

    def run(self):

        if len(self.args)>=1:
            name = self.args[0]
            pisi.toplevel.remove_repo(name)
        else:
            self.help()
            return

class ListRepo(Command):
    """List repositories

    Usage:
    list-repo

TODO: Some description...
"""
    def __init__(self):
        super(ListRepo, self).__init__()

    def run(self):

        from pisi.repodb import repodb
        for repo in repodb.list():
            print repo
            print '  ', repodb.get_repo(repo).indexuri.getUri()


class ListAvailable(Command):
    """List available packages in the repositories

    Usage:
    list-available [repo]

TODO: desc...
"""
    def __init__(self):
        super(ListAvailable, self).__init__()
    
    def run(self):
        from pisi.repodb import repodb
        from pisi.ui import ui

        self.init_db()

        if self.args:
            for arg in self.args:
                self.print_packages(arg)
        else:
            # print for all repos
            for repo in repodb.list():
                ui.info("Repository : %s\n" % repo)
                self.print_packages(repo)

    def print_packages(self, repo):
        from pisi import packagedb

        pkg_db = packagedb.get_db(repo)
        for p in pkg_db.list_packages():
            print p


class ListPending(Command):
    """List pending packages"""
    
    def __init__(self):
        super(ListPending, self).__init__()
    
    def run(self):
        from pisi.installdb import installdb
        from pisi.ui import ui

        self.init_db()

        for p in installdb.list_pending():
            print p


class SearchAvailable(Command):
    """Search in available packages

    Usage:
    search-available <search pattern>

TODO: Some description...
"""
    pass


# Partial build commands        

class BuildUntil(Command):
    """Run the build process partially

    Usage:
    -sStateName build-until <pspec file>

    Where states are:
    unpack, setupaction, buildaction, installaction, buildpackages

You can give an URI of the pspec.xml file. PISI will fetch all
necessary files and unpack the source and prepare a source directory
for you.
"""
    def __init__(self):
        super(BuildUntil, self).__init__()

    def options(self):
        self.parser.add_option("-s", action="store", dest="state")

    def run(self):
        if not self.args:
            self.help()
            return

        state = self.options.state

        for arg in self.args:
            pisi.toplevel.build_until(arg, state, self.authInfo)

class BuildUnpack(Command):
    """Unpack the source archive

    Usage:
    build-dounpack <pspec file>

TODO: desc.
"""
    def __init__(self):
        super(BuildUnpack, self).__init__()

    def run(self):
        if not self.args:
            self.help()
            return

        for arg in self.args:
            pisi.toplevel.build_until(arg, "unpack", self.authInfo)


class BuildSetup(Command):
    """Setup the source

    Usage:
    build-dosetup <pspec file>

TODO: desc.
"""
    def __init__(self):
        super(BuildSetup, self).__init__()

    def run(self):
        if not self.args:
            self.help()
            return

        for arg in self.args:
            pisi.toplevel.build_until(arg, "setupaction", self.authInfo)


class BuildBuild(Command):
    """Setup the source

    Usage:
    build-dobuild <pspec file>

TODO: desc.
"""
    def __init__(self):
        super(BuildBuild, self).__init__()

    def run(self):
        if not self.args:
            self.help()
            return

        for arg in self.args:
            pisi.toplevel.build_until(arg, "buildaction", self.authInfo)

class BuildInstall(Command):
    """Install to the sandbox

    Usage:
    build-doinstall <pspec file>

TODO: desc.
"""
    def __init__(self):
        super(BuildInstall, self).__init__()

    def run(self):
        if not self.args:
            self.help()
            return

        for arg in self.args:
            pisi.toplevel.build_until(arg, "installaction", self.authInfo)

class BuildPackage(Command):
    """Setup the source

    Usage:
    build-dobuild <pspec file>

TODO: desc.
"""
    def __init__(self):
        super(BuildPackage, self).__init__()

    def run(self):
        if not self.args:
            self.help()
            return

        for arg in self.args:
            pisi.toplevel.build_until(arg, "buildpackages", self.authInfo)
