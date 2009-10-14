import unittest
import os

from pisi import util
from pisi import package
import pisi.context as ctx

class PackageTestCase(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.pkgName = util.package_name('test','7.1','2',3)

    def testAddPackage(self):
        cur = os.getcwd()
        tmp = ctx.config.tmp_dir()
        test = os.path.join(cur, 'history')
        pkg_path = os.path.join(tmp, self.pkgName)
        pkg = package.Package(pkg_path, "w")

        os.chdir(test)
        pkg.add_to_package('002_remove.xml')
        pkg.add_to_package('003_install.xml')
        os.chdir(cur)
        pkg.close()

        pkg = package.Package(pkg_path)
        pkg.extract_file('002_remove.xml', cur)
        if os.path.exists('files.xml'):
            self.fail("Package add error")

        os.remove('002_remove.xml')
        os.remove(pkg_path)

    def testExtractFile(self):
        cur = os.getcwd()
        tmp = ctx.config.tmp_dir()
        pkg_path = os.path.join(tmp, self.pkgName)
        pkg = package.Package(pkg_path,"w")
        pkg.extract_file("files.xml",cur)
        if os.path.exists("files.xml"):
            self.fail("File extract error")
        pkg.extract_pisi_files("002_remove.xml")
        if os.path.exists("002_remove.xml"):
            self.fail("Pisi files extract error")

