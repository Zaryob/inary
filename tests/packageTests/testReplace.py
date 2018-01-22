import unittest
import inary.data.replace
import inary.data.relation

class ReplaceTestCase(unittest.TestCase):
    def testInstalledPackageReplaced(self):
        inary.api.install(["ethtool"])
        relation = inary.data.relation.Relation()
        relation.package = "ethtool"
        relation.version = "6"
        relation.release = "1"

        replace = inary.data.replace.Replace(relation)
        replace.package = "zlib"
        # Check if the replaced package is installed
        self.assertTrue(inary.data.replace.installed_package_replaced(replace))
        repinfo = inary.data.replace.Replace(relation)
        repinfo.package = "ctorrent"
        assert not inary.data.replace.installed_package_replaced(repinfo)

        inary.api.remove(["ethtool"])
