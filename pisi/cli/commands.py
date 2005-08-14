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
from pisi.purl import PUrl
from pisi.cli.common import *


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
        self.parser = commonopts(self.parser)
        (self.options, self.args) = self.parser.parse_args()
        #print 'opts,args = ', self.options, self.args
        self.args.pop(0)                # exclude command arg

        import pisi

        # initialize PiSi
        pisi.config.config = pisi.config.Config(self.options)
        pisi.ui.ui = pisi.ui.CLI(self.options.debug)
        
        self.check_auth_info()

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
        
        # IMPORTANT: command imports here or in the command class run fxns
        import pisi.toplevel
        from pisi.ui import ui

        if database:
            from pisi.repodb import repodb
            repodb.init_dbs()

    def finalize(self):
        pass

    def help(self):
        self.parser.print_help()
        #print getattr(self, "__doc__")

    def die(self):
        print 'Program terminated abnormally.'
        sys.exit(-1)


class Help(Command):
    """Prints help for a given command

    Usage:
    help [command-name]

If run without parameters will print the general usage documentation.

If run with a command name as the parameter will print the documentation
for that command, where command is one of: 

"""

    def __init__(self):
        self.__doc__ = usage_text
        super(Help, self).__init__()

    def run(self):
        if not self.args:
            self.parser.set_usage(usage_text)
            self.parser.print_help()
            return
            
        self.init()
        
        for arg in self.args:
            print
            pisi.ui.ui.info("command: %s\n" % arg)
            obj = get_command(arg, True)
            obj.help()
        
        self.finalize()

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

        self.init()
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

    Usage:
    install package1 package2 ... packagen

You may use filenames, URIs or package names for packages. If you have
specified a package name, it should exist in a specified repository.
"""
    def __init__(self):
        super(Install, self).__init__()

    def run(self):
        if not self.args:
            self.help()
            return

        self.init()
        pisi.toplevel.install(self.args)
        self.finalize()


class Upgrade(PackageOp):
    """Upgrade PISI packages

    Usage:
    Upgrade package1 package2 ... packagen

You may use filenames, URIs or package names for packages. If you have
specified a package name, it should exist in a specified repository.
"""
    def __init__(self):
        super(Upgrade, self).__init__()

    def run(self):
        if not self.args:
            self.help()
            return

        self.init()
        pisi.toplevel.upgrade(self.args)
        self.finalize()


class Remove(PackageOp):
    """Remove PISI packages

    Usage:
    remove package1-name package2-name ... packagen-name

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
        super(ConfigurePending, self).__init__()

    def run(self):

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

    Usage:
    index directory

TODO: Some description...
"""
    def __init__(self):
        super(Index, self).__init__()

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
        self.init(True)
        from pisi.installdb import installdb
        for pkg in installdb.list_installed():
            package = pisi.packagedb.get_package(pkg)
            if not self.options.long:
                print package.name, '-', package.summary
            else:
                print package
        self.finalize()


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

        self.init(True)
        for repo in self.args:
            pisi.toplevel.update_repo(repo)
        self.finalize()

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
            self.init()
            name = self.args[0]
            indexuri = self.args[1]
            pisi.toplevel.add_repo(name, indexuri)
            self.init()
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
            self.init()
            name = self.args[0]
            pisi.toplevel.remove_repo(name)
            self.finalize()
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

        self.init()
        from pisi.repodb import repodb
        for repo in repodb.list():
            print repo
            print '  ', repodb.get_repo(repo).indexuri.getUri()
        self.finalize()


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
        for p in pkg_db.list_packages():
            print p


class ListPending(Command):
    """List pending packages"""
    
    def __init__(self):
        super(ListPending, self).__init__()
    
    def run(self):
        from pisi.installdb import installdb
        from pisi.ui import ui

        self.init(True)

        for p in installdb.list_pending():
            print p

        self.finalize()

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

        self.init()
        state = self.options.state

        for arg in self.args:
            pisi.toplevel.build_until(arg, state, self.authInfo)
        self.finalize()


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

        self.init()
        for arg in self.args:
            pisi.toplevel.build_until(arg, "unpack", self.authInfo)
        self.finalize()


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

        self.init()
        for arg in self.args:
            pisi.toplevel.build_until(arg, "setupaction",
                                      self.authInfo)
        self.finalize()


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

        self.init()
        for arg in self.args:
            pisi.toplevel.build_until(arg, "buildaction", self.authInfo)
        self.finalize()


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

        self.init()
        for arg in self.args:
            pisi.toplevel.build_until(arg, "installaction",
                                      self.authInfo)
        self.finalize()


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

usage_text = (usage_text1 + commands_string() + usage_text2)

