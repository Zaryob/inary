import unittest
import inary.relation
import inary.dependency

class DependencyTestCase(unittest.TestCase):

    def testDictSatisfiesDep(self):
        inary.api.install(["ethtool"])
        relation = inary.relation.Relation()
        relation.package = "ethtool"

        inary.api.install(["zlib"])
        rel = inary.relation.Relation()
        rel.package = "zlib"

        depinfo = inary.dependency.Dependency(relation)
        dictionary = {"ethtool": [" "],"zlib":["a","b"],"ctorrent":["c"]}
        assert not depinfo.satisfied_by_dict_repo(dictionary)
        depinf = inary.dependency.Dependency(rel)
        assert not depinf.satisfied_by_dict_repo(dictionary)

    def testInstalledSatisfiesDep(self):
        inary.api.install(["ctorrent"])
        relation = inary.relation.Relation()
        relation.package = "ctorrent"
        depinfo = inary.dependency.Dependency(relation)
        assert not depinfo.satisfied_by_installed()

    def testRepoSatisfiesDependency(self):
        inary.api.install(["ethtool"])
        relation = inary.relation.Relation()
        relation.package = "ctorrent"
        depinfo = inary.dependency.Dependency(relation)
        assert not depinfo.satisfied_by_repo()
