import unittest
import inary.data.relation
import inary.analyzer.dependency

class DependencyTestCase(unittest.TestCase):

    def testDictSatisfiesDep(self):
        inary.api.install(["ethtool"])
        relation = inary.data.relation.Relation()
        relation.package = "ethtool"

        inary.api.install(["zlib"])
        rel = inary.data.relation.Relation()
        rel.package = "zlib"

        depinfo = inary.analyzer.dependency.Dependency(relation)
        dictionary = {"ethtool": [" "],"zlib":["a","b"],"ctorrent":["c"]}
        assert not depinfo.satisfied_by_dict_repo(dictionary)
        depinf = inary.analyzer.dependency.Dependency(rel)
        assert not depinf.satisfied_by_dict_repo(dictionary)

    def testInstalledSatisfiesDep(self):
        inary.api.install(["ctorrent"])
        relation = inary.data.relation.Relation()
        relation.package = "ctorrent"
        depinfo = inary.analyzer.dependency.Dependency(relation)
        assert not depinfo.satisfied_by_installed()

    def testRepoSatisfiesDependency(self):
        inary.api.install(["ethtool"])
        relation = inary.data.relation.Relation()
        relation.package = "ctorrent"
        depinfo = inary.analyzer.dependency.Dependency(relation)
        assert not depinfo.satisfied_by_repo()
