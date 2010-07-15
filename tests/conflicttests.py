# -*- coding: utf-8 -*-
import unittest
import pisi
import pisi.context as ctx
import pisi.conflict

class ConflictTestCase(unittest.TestCase):

    def testInstalledPackageConflicts(self):
        pisi.api.install(["ethtool"])
        confinfo = pisi.conflict.Conflict()
        confinfo.package = "ethtool"
        confinfo.version = "6"
        confinfo.release = "1"
        assert not pisi.conflict.installed_package_conflicts(confinfo)
        pisi.api.remove(["ethtool"])

    def testCalculateConflicts(self):
        packagedb = pisi.db.packagedb.PackageDB()
        packages = ["ethtool", "zlib", "ctorrent"]
        assert pisi.conflict.calculate_conflicts(packages, packagedb)

    def testConflictCheck(self):
        # In our sample repo1, spam conflicts with bar.
        # If this fails, it may affect database test case results.
        pisi.api.add_repo("repo1", "repos/repo1-bin/pisi-index.xml")
        pisi.api.update_repo("repo1")
        pisi.api.install(["spam"])

        myconflict = pisi.conflict.Conflict()
        myconflict.package = "bar"
        myconflict.version = "0.3"
        myconflict.release = "1"

        pisi.api.install(["bar"])
        assert "bar" in pisi.api.list_installed()
        assert "spam" not in pisi.api.list_installed()

        pisi.api.remove(["bar"])
        pisi.api.remove_repo("repo1")

    def testInterRepoCrossConflicts(self):
        #If this fails, it may affect database test case results
        pisi.api.add_repo("repo1", "repos/repo1-bin/pisi-index.xml")
        pisi.api.update_repo("repo1")

        pisi.api.install(["spam", "foo"])
        before = pisi.api.list_installed()
        pisi.api.remove_repo("repo1")

        pisi.api.add_repo("repo2", "repos/repo2-bin/pisi-index.xml")
        pisi.api.update_repo("repo2")
        pisi.api.upgrade(["spam"])
        after = pisi.api.list_installed()

        assert set(before) == set(after)

        idb = pisi.db.installdb.InstallDB()
        assert 3 == int(idb.get_package("foo").release)

        pisi.api.remove(["foo"])
        pisi.api.remove(["spam"])
        pisi.api.remove_repo("repo2")
