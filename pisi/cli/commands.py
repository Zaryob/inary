import sys
from optparse import OptionParser
import pisi
from pisi.config import config
from pisi.purl import PUrl
from common import *
import pisi.toplevel

# helper functions
def cmdObject(cmd, fail=False):
    commands = {"help": Help,
                "build": Build,
                "info": Info,
                "install": Install,
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

        for arg in self.args:
            pisi.toplevel.build(arg, self.authInfo)

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

        self.init_db()
        pisi.toplevel.install(self.args)

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

        self.init_db()
        pisi.toplevel.remove(self.args)

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
            metadata, files = pisi.toplevel.info(arg)
            print metadata.package

class Index(Command):
    """index: Index PISI files in a given directory"""
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
    """list-installed: print a list of all installed packages  
    usage: list-installed """

    def __init__(self):
        super(ListInstalled, self).__init__()

    def options(self):
        self.parser.add_option("-l", "--long", action="store_true",
                               default=False, help="show in long format")

    def run(self):
        self.init_db()
        from pisi.installdb import installdb
        for pkg in installdb.list_installed():
            from pisi.packagedb import packagedb
            package = packagedb.get_package(pkg)
            if not self.options.long:
                print package.name, '-', package.summary
            else:
                print package

class UpdateRepo(Command):
    """update-repo: update the databases of a repository
    usage: update-repo <repo1> <repo2> ...."""
    def __init__(self):
        super(UpdateRepo, self).__init__()

    def run(self):
        self.init_db()
        for repo in self.args:
            pisi.toplevel.update_repo(repo)

class AddRepo(Command):
    """add-repo: add a repository
    usage: add-repo <repo> <indexuri>"""
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
    """remove-repo: remove a repository
    usage: remove-repo <repo>"""
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
    """list-repo: list repositories"""
    def __init__(self):
        super(ListRepo, self).__init__()

    def run(self):

        from pisi.repodb import repodb
        for repo in repodb.list():
            print repo
            print '  ', repodb.get_repo(repo).indexuri.getUri()

class ListAvailable(Command):
    "list-available: list the available packages in the repository"
    def __init__(self):
        super(ListAvailable, self).__init__()

    def run(self):
        self.init_db()
        from pisi import util
        # FIXME: bu asagidaki code bayagi anlamsiz
        # neden bir packagedb'miz var?
        (repo, index) = util.repo_index()

        for package in index.packages:
            name = package.name
            version = package.history[0].version
            release = package.history[0].release

            print util.package_name(name, version, release)

class SearchAvailable(Command):
    "search-available: search in available packages"
    pass

        
