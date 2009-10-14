import unittest
import pisi
import pisi.relation
import pisi.conflict

class ConflictTestCase(unittest.TestCase):
    def testInstalledPackageConflicts(self):
        pisi.api.install(["ethtool"])
        relation = pisi.relation.Relation()
        relation.package = "ethtool"
        relation.version = "6"
        relation.release = "1"

        confinfo = pisi.conflict.Conflict(relation)
        assert not pisi.conflict.installed_package_conflicts(confinfo)

    def testCalculateConflicts(self):
        packagedb = pisi.db.packagedb.PackageDB()
        packages = ["ethtool", "zlib", "ctorrent"]
        assert pisi.conflict.calculate_conflicts(packages, packagedb)

  



