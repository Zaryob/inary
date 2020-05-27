import unittest
import inary.constants
import inary.context as ctx


class ConstantTestCase(unittest.TestCase):

    def testConstants(self):
        constants = ctx.const
        constDict = {
            "actions": "actions.py",
            "setup": "setup",
            "metadata": "metadata.xml"}

        for i in list(constDict.keys()):
            if hasattr(constants, i):
                value = getattr(constants, i)
                self.assertEqual(value, constDict[i])
