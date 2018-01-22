import unittest
import inary.data.relation
import inary.analyzer.dependency

class DependencyTestCase(unittest.TestCase):

    def testDictSatisfiesDep(self):
        inary.api.install(["uif2iso"])
        relation = inary.data.relation.Relation()
        relation.package = "uif2iso"

        inary.api.install(["minizip"])
        rel = inary.data.relation.Relation()
        rel.package = "minizip"

        depinfo = inary.analyzer.dependency.Dependency(relation)
        dictionary = {"ethtool": [" "],"minizip":["zlib"]}
        assert not depinfo.satisfied_by_dict_repo(dictionary)
        depinf = inary.analyzer.dependency.Dependency(rel)
        assert not depinf.satisfied_by_dict_repo(dictionary)

    def testInstalledSatisfiesDep(self):
        inary.api.install(["uif2iso"])
        relation = inary.data.relation.Relation()
        relation.package = "uif2iso"
        depinfo = inary.analyzer.dependency.Dependency(relation)
        assert not depinfo.satisfied_by_installed()

    def testRepoSatisfiesDependency(self):
        inary.api.install(["uif2iso"])
        relation = inary.data.relation.Relation()
        relation.package = "uif2iso"
        depinfo = inary.analyzer.dependency.Dependency(relation)
        assert not depinfo.satisfied_by_repo()
