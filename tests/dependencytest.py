import unittest
import pisi.relation
import pisi.dependency

class DependencyTestCase(unittest.TestCase):

    def testDictSatisfiesDep(self):
        pisi.api.install(["ethtool"])
        relation = pisi.relation.Relation()
        relation.package = "ethtool"

        pisi.api.install(["zlib"])
        rel = pisi.relation.Relation()
        rel.package = "zlib"

        depinfo = pisi.dependency.Dependency(relation)
        dictionary = {"ethtool": [" "],"zlib":["a","b"],"ctorrent":["c"]}
        assert not depinfo.satisfied_by_dict_repo(dictionary)
        depinf = pisi.dependency.Dependency(rel)
        assert not depinf.satisfied_by_dict_repo(dictionary)

    def testInstalledSatisfiesDep(self):
        pisi.api.install(["ctorrent"])
        relation = pisi.relation.Relation()
        relation.package = "ctorrent"
        depinfo = pisi.dependency.Dependency(relation)
        assert not depinfo.satisfied_by_installed()

    def testRepoSatisfiesDependency(self):
        pisi.api.install(["ethtool"])
        relation = pisi.relation.Relation()
        relation.package = "ctorrent"
        depinfo = pisi.dependency.Dependency(relation)
        assert not depinfo.satisfied_by_repo()
