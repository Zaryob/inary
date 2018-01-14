
import unittest
import inary.relation

class RelationTestCase(unittest.TestCase):
    def testInstalledPackageSatisfies(self):
        inary.api.install(["ethtool"])
        relation = inary.relation.Relation()

        relation.package = "ethtool"
        # Test version = X
        relation.version = "0.3"
        assert inary.relation.installed_package_satisfies(relation)
        relation.version = None

        # Test versionFrom = X
        relation.versionFrom = "0.3"
        assert inary.relation.installed_package_satisfies(relation)
        relation.versionFrom = "8"
        assert not inary.relation.installed_package_satisfies(relation)
        relation.versionFrom = None
        
        #Test versionTo = X
        relation.versionTo = "8"
        assert inary.relation.installed_package_satisfies(relation)
        relation.versionTo = "0.1"
        assert not inary.relation.installed_package_satisfies(relation)
        relation.versionTo = None
        
        #Test release = X
        relation.release = "3"
        assert not inary.relation.installed_package_satisfies(relation)
        relation.release = "1"
        assert inary.relation.installed_package_satisfies(relation)
        relation.release = None

        #test releaseFrom = X
        relation.releaseFrom = "1"
        assert inary.relation.installed_package_satisfies(relation)
        relation.releaseFrom = "7"
        assert not inary.relation.installed_package_satisfies(relation)
        relation.releaseFrom = None

        #test releaseTo = X
        relation.releaseTo = "7"
        assert inary.relation.installed_package_satisfies(relation)
        relation.releaseTo = "0"
        assert not inary.relation.installed_package_satisfies(relation)
        relation.releaseTo = None

        inary.api.remove(["ethtool"])

