import unittest
import inary.replace
import inary.relation

class ReplaceTestCase(unittest.TestCase):
    def testInstalledPackageReplaced(self):
        inary.api.install(["ethtool"])
        relation = inary.relation.Relation()
        relation.package = "ethtool"
        relation.version = "6"
        relation.release = "1"

        replace = inary.replace.Replace(relation)
        replace.package = "zlib"
        # Check if the replaced package is installed
        self.assertTrue(inary.replace.installed_package_replaced(replace))
        repinfo = inary.replace.Replace(relation)
        repinfo.package = "ctorrent"
        assert not inary.replace.installed_package_replaced(repinfo)

        inary.api.remove(["ethtool"])
