# Author: Eray Ozkural

class RepoDB(object):
    """RepoDB maps repo ids to distribution information"""
    def __init__(self):
        filename = os.path.join(config.db_dir(), 'repo.bdb')
        self.d = shelve.open(filename)
        self.fdummy = open(filename)
        fcntl.flock(self.fdummy, fcntl.LOCK_EX)

    def __del__(self):
        #fcntl.flock(self.fdummy, fcntl.LOCK_UN)
        self.fdummy.close()

    def has_distro(self, name):
        name = str(name)
        return self.d.has_key(name)

    def get_distro(self, name):
        name = str(name)
        return self.d[name]

    def add_distro(self, dist_info):
        name = str(dist_info.name)
        self.d[name] = dist_info

    def clear(self):
        self.d.clear()

    def remove_repo(self, name):
        name = str(name)
        del self.d[name]

repodb = RepoDB()
