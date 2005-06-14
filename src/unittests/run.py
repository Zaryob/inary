#!/usr/bin/python

import unittest
import sys
sys.path.append(".")

runTestSuite = lambda(x): unittest.TextTestRunner(verbosity=2).run(x)

def run_all():
    import specfiletests
    import fetchertests
    import archivetests

    alltests = unittest.TestSuite((
	specfiletests.suite,
	fetchertests.suite,
	archivetests.suite
	))

    runTestSuite(alltests)

if __name__ == "__main__":
    args = sys.argv
    if len(args) > 1: # run modules given from the command line
	tests = sys.argv[1:]
	for test in tests:
	    module = __import__(test)
	    print "\nRunning tests in '%s'...\n" % (test)
	    runTestSuite(module.suite)

    else: # run all tests
	print "\nRunning all test in an order...\n"
	run_all()
