
import unittest

from pisi.constants import const 

class ContextTestCase(unittest.TestCase):
    
    def testConstness(self):
        # test if we can get a const attribute?
        try:
            test = const.archives_dir_suffix
            self.assertNotEqual(test, "")
        except AttributeError:
            self.fail("Couldn't get const attribute")

        # test binding a new constant
        const.test = "test binding"
    
        # test re-binding (which is illegal)
        try:
            const.test = "test rebinding"
            # we shouldn't reach here
            self.fail("Rebinding a constant works. Something is wrong!")
        except:
            # we achived our goal with this error. infact, this is a
            # ConstError but we can't catch it directly here
            pass

        # test unbinding (which is also illegal)
        try:
            del const.test
            # we shouldn't reach here
            self.fail("Unbinding a constant works. Something is wrong!")
        except:
            # we achived our goal with this error. infact, this is a
            # ConstError but we can't catch it directly here
            pass
suite = unittest.makeSuite(ContextTestCase)
