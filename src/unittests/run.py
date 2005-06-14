#!/usr/bin/python

import unittest
import sys
sys.path.append(".")

import specfiletests
import fetchertests
import archivetests

def main():
    alltests = unittest.TestSuite((
	specfiletests.suite,
	fetchertests.suite,
	archivetests.suite
	))

    unittest.TextTestRunner(verbosity=2).run(alltests)

if __name__ == "__main__":
    main()
