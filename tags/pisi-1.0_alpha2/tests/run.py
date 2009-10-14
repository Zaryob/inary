#!/usr/bin/python
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import unittest
import sys
import os

sys.path.append('.')
sys.path.append('..')

runTestSuite = lambda(x): unittest.TextTestRunner(verbosity=2).run(x)

def run_all():

    import utiltests
    import xmlfiletests
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
    import packagetests

    alltests = unittest.TestSuite((
        utiltests.suite, 
        xmlfiletests.suite,
        specfiletests.suite,
        metadatatests.suite,
        constantstests.suite,
        fetchertests.suite,
        archivetests.suite,
        installdbtests.suite,
        sourcedbtests.suite,
        packagedbtests.suite,
# FIXME: actionsapitests requires tester to run a specific command first.
#        actionsapitests.suite,
        graphtests.suite,
        versiontests.suite,
        configfiletests.suite,
        packagetests.suite
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
