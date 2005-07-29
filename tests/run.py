#!/usr/bin/python

import unittest
import sys
import os

sys.path.append('.')

runTestSuite = lambda(x): unittest.TextTestRunner(verbosity=2).run(x)

def run_all():

    import utiltests
    import specfiletests
    import metadatatests
    import constantstests
    import fetchertests
    import archivetests
    import installdbtests
    import sourcedbtests
    import packagedbtests
    import actionsapitests
    import graphtests
    import versiontests
    import configfiletests

    alltests = unittest.TestSuite((
        utiltests.suite, 
        specfiletests.suite,
        specfiletests.suite,
        metadatatests.suite,
        constantstests.suite,
        fetchertests.suite,
        archivetests.suite,
        installdbtests.suite,
        sourcedbtests.suite,
        packagedbtests.suite,
        actionsapitests.suite,
        graphtests.suite,
        versiontests.suite,
        configfiletests.suite
        ))

    runTestSuite(alltests)

if __name__ == "__main__":
    args = sys.argv
    if len(args) > 1: # run modules given from the command line
        tests = sys.argv[1:]
        for test in tests:
            module = __import__(test + 'tests')
            print "\nRunning tests in '%s'...\n" % (test)
            runTestSuite(module.suite)
    else: # run all tests
        print "\nRunning all tests in order...\n"
        run_all()
