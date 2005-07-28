# Author: Eray Ozkural

from bsddb import db
import bsddb.dbshelve as shelve
import os, fcntl

from config import config
import packagedb, util
from pisi.purl import PUrl

class Repo:
    def __init__(self, indexuri):
        self.indexuri = indexuri
        
class RepoDB(object):
    """RepoDB maps repo ids to repository information"""
    def __init__(self):
        self.filename = os.path.join(config.db_dir(), 'repo.bdb')
        self.d = shelve.open(self.filename)
        self.fdummy = open(self.filename + '.lock', 'w')
        fcntl.flock(self.fdummy, fcntl.LOCK_EX)

    def init_dbs(self):
        # initialize package/source dbs
        for x in self.d.keys():
            packagedb.add_db(x)

    def __del__(self):
        #fcntl.flock(self.fdummy, fcntl.LOCK_UN)
        self.fdummy.close()
        #os.unlink(self.filename + '.lock')

    def has_repo(self, name):
        name = str(name)
        return self.d.has_key(name)

    def get_repo(self, name):
        name = str(name)
        return self.d[name]

    def add_repo(self, name, repo_info):
        self.d[name] = repo_info
        packagedb.add_db(name)

    def list(self):
        return self.d.keys()

    def clear(self):
        self.d.clear()

    def remove_repo(self, name):
        name = str(name)
        del self.d[name]

repodb = RepoDB()
