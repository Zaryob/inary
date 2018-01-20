# -*- coding: utf-8 -*-
import unittest
import inary
import inary.context as ctx
import inary.analyzer.conflict

class ConflictTestCase(unittest.TestCase):

    def testInstalledPackageConflicts(self):
        inary.api.install(["ethtool"])
        confinfo = inary.analyzer.conflict.Conflict()
        confinfo.package = "ethtool"
        confinfo.version = "6"
        confinfo.release = "1"
        assert not inary.analyzer.conflict.installed_package_conflicts(confinfo)
        inary.api.remove(["ethtool"])

    def testCalculateConflicts(self):
        packagedb = inary.db.packagedb.PackageDB()
        packages = ["ethtool", "zlib", "ctorrent"]
        assert inary.analyzer.conflict.calculate_conflicts(packages, packagedb)

    def testConflictCheck(self):
        # In our sample repo1, inary.analyzer.conflicts with bar.
        # If this fails, it may affect database test case results.
        inary.api.add_repo("repo1", "repos/repo1-bin/inary-index.xml")
        inary.api.update_repo("repo1")
        inary.api.install(["inary"])

        myconflict = inary.analyzer.conflict.Conflict()
        myconflict.package = "bar"
        myconflict.version = "0.3"
        myconflict.release = "1"

        inary.api.install(["bar"])
        assert "bar" in inary.api.list_installed()
        assert "inary" not in inary.api.list_installed()

        inary.api.remove(["bar"])
        inary.api.remove_repo("repo1")

    def testInterRepoCrossConflicts(self):
        #If this fails, it may affect database test case results
        inary.api.add_repo("repo1", "repos/repo1-bin/inary-index.xml")
        inary.api.update_repo("repo1")

        inary.api.install(["inary", "foo"])
        before = inary.api.list_installed()
        inary.api.remove_repo("repo1")

        inary.api.add_repo("repo2", "repos/repo2-bin/inary-index.xml")
        inary.api.update_repo("repo2")
        inary.api.upgrade(["inary"])
        after = inary.api.list_installed()

        assert set(before) == set(after)

        idb = inary.db.installdb.InstallDB()
        assert 3 == int(idb.get_package("foo").release)

        inary.api.remove(["foo"])
        inary.api.remove(["inary"])
        inary.api.remove_repo("repo2")
