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
        assert not pisi.dependency.dict_satisfies_dep(dictionary,depinfo)
        depinf = pisi.dependency.Dependency(rel)
        assert not pisi.dependency.dict_satisfies_dep(dictionary,depinf)

    def testInstalledSatisfiesDep(self):
        pisi.api.install(["ctorrent"])
        relation = pisi.relation.Relation()
        relation.package = "ctorrent"
        depinfo = pisi.dependency.Dependency(relation)
        assert not pisi.dependency.installed_satisfies_dep(depinfo)

    def testRepoSatisfiesDependency(self):
        pisi.api.install(["ethtool"])
        relation = pisi.relation.Relation()
        relation.package = "ctorrent"
        depinfo = pisi.dependency.Dependency(relation)
        assert not pisi.dependency.repo_satisfies_dep(depinfo)

    def testSatisfiesRuntimeDeps(self):
        pisi.api.install(["ethtool"])
        assert pisi.dependency.satisfies_runtime_deps("ethtool")
        pisi.api.install(["ctorrent"])
        assert pisi.dependency.satisfies_runtime_deps("ctorrent")

    def testInstallable(self):
        assert pisi.dependency.installable("zlib")
        assert pisi.dependency.installable("ethtool")
        assert not pisi.dependency.installable("paket")
