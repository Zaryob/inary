
import unittest

from pisi import context

class ContextTestCase(unittest.TestCase):
    def setUp(self):
	self.ctx = context.Context("../popt/popt.pspec")
	
    def testConstness(self):

	# test if we can get a const attribute?
	try:
	    test = self.ctx.const.archives_dir_suffix
	    self.assertNotEqual(test, "")
	except AttributeError:
	    self.fail("Couldn't get const attribute")

	# test binding a new constant
	self.ctx.const.test = "test binding"
	
	# test re-binding (which is illegal)
	try:
	    self.ctx.const.test = "test rebinding"
	    # we shouldn't reach here
	    self.fail("Rebinding a constant works. Something is wrong!")
	except:
	    # we achived our goal with this error. infact, this is a
	    # ConstError but we can't catch it directly here
	    pass

	# test unbinding (which is also illegal)
	try:
	    del self.ctx.const.test
	    # we shouldn't reach here
	    self.fail("Unbinding a constant works. Something is wrong!")
	except:
	    # we achived our goal with this error. infact, this is a
	    # ConstError but we can't catch it directly here
	    pass
    
	    

suite = unittest.makeSuite(ContextTestCase)
