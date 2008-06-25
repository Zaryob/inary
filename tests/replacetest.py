import unittest
import pisi.replace
import pisi.relation

class ReplaceTestCase(unittest.TestCase):
    def testInstalledPackageReplaced(self):
        pisi.api.install(["ethtool"])
        relation = pisi.relation.Relation()
        relation.package = "ethtool"
        relation.version = "6"
        relation.release = "1"

        replace = pisi.replace.Replace(relation)
        replace.package = "zlib"
        assert pisi.replace.installed_package_replaced(replace)
        repinfo = pisi.replace.Replace(relation)
        repinfo.package = "ctorrent"
        assert not pisi.replace.installed_package_replaced(repinfo)

        pisi.api.remove(["ethtool"])
