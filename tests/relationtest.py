
import unittest
import pisi.relation

class RelationTestCase(unittest.TestCase):
    def testInstalledPackageSatisfies(self):
        pisi.api.install(["ethtool"])
        relation = pisi.relation.Relation()

        relation.package = "ethtool"
        # Test version = X
        relation.version = "6"
        assert pisi.relation.installed_package_satisfies(relation)
        relation.version = None

        # Test versionFrom = X
        relation.versionFrom = "3"
        assert pisi.relation.installed_package_satisfies(relation)
        relation.versionFrom = "8"
        assert not pisi.relation.installed_package_satisfies(relation)
        relation.versionFrom = None
        
        #Test versionTo = X
        relation.versionTo = "8"
        assert pisi.relation.installed_package_satisfies(relation)
        relation.versionTo = "3"
        assert not pisi.relation.installed_package_satisfies(relation)
        relation.versionTo = None
        
        #Test release = X
        relation.release = "3"
        assert pisi.relation.installed_package_satisfies(relation)
        relation.release = "1"
        assert not pisi.relation.installed_package_satisfies(relation)
        relation.release = None

        #test releaseFrom = X
        relation.releaseFrom = "1"
        assert pisi.relation.installed_package_satisfies(relation)
        relation.releaseFrom = "7"
        assert not pisi.relation.installed_package_satisfies(relation)
        relation.releaseFrom = None

        #test releaseTo = X
        relation.releaseTo = "7"
        assert pisi.relation.installed_package_satisfies(relation)
        relation.releaseTo = "1"
        assert not pisi.relation.installed_package_satisfies(relation)
        relation.releaseTo = None

        pisi.api.remove(["ethtool"])

