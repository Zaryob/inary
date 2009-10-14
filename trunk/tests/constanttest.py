import unittest
import pisi.constants
import pisi.context as ctx

class ConstantTestCase(unittest.TestCase):

    def testConstants(self):
        constants = ctx.const
        constDict = {"actions": "actions.py", "setup":"setup","metadata":"metadata.xml"}

        for i in constDict.keys():
            if hasattr(constants,i):
                value = getattr(constants,i)
                self.assertEqual(value, constDict[i])
    
