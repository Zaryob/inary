#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import time
import shutil

import unittest
from unittest import _TextTestResult

import inary
import inary.api
import inary.context as ctx
import inary.util as util
import os


def importTest(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def getTests(path, base_path, files=''):
    if not files:
        files = os.listdir(path)
        files = sorted(
            [f[:-3] for f in files if f.startswith("test") and f.endswith(".py")])
    parent_path = path[len(base_path) + 1:]
    parent_module = parent_path.replace('/', '.')
    result = []
    for mymodule in files:
        modname = ".".join((parent_module, mymodule))
        mod = importTest(modname)
        result.append(unittest.TestLoader().loadTestsFromModule(mod))
    return result


class TextTestResult(_TextTestResult):
    def __init__(self, stream, descriptions, verbosity):
        super(TextTestResult, self).__init__(stream, descriptions, verbosity)
        self.todoed = []

    def addTodo(self, test, info):
        self.todoed.append((test, info))
        if self.showAll:
            self.stream.writeln("TODO")
        elif self.dots:
            self.stream.write(".")

    def printErrors(self):
        if self.dots or self.showAll:
            self.stream.writeln()
            self.printErrorList(util.colorize('ERROR', 'red'), self.errors)
            self.printErrorList(util.colorize('FAIL', 'blue'), self.failures)
            self.printErrorList(util.colorize('TODO', 'purple'), self.todoed)


class InaryTestRunner(unittest.TextTestRunner):

    def Result(self):
        return TextTestResult(self.stream, self.descriptions, self.verbosity)

    def run(self, Test, retresult=True):
        """
        Run the given test case or test suite.
        """
        result = self.Result()
        startTime = time.time()
        Test(result)
        stopTime = time.time()
        timeTaken = stopTime - startTime
        if retresult == True:
            result.printErrors()
        self.stream.writeln(result.separator2)
        run = result.testsRun
        self.stream.write(
            util.colorize(
                "\n\n====== COMPLATE TESTS =======\n",
                'yellow'))
        self.stream.writeln(util.colorize("  * Runned %d test%s in %.3fs" %
                                          (run, run != 1 and "s" or "", timeTaken), 'blue'))
        self.stream.writeln()
        if not result.wasSuccessful():
            failed = len(result.failures)
            errored = len(result.errors)
            todoed = len(result.todoed)
            success = run - (failed + errored + todoed)
            self.stream.write(
                util.colorize(
                    "    => %d Successed\n" %
                    success, 'green'))
            if failed:
                self.stream.write(
                    util.colorize(
                        "\n    => %d Failures\n" %
                        failed, 'red'))
            if errored:
                self.stream.write(
                    util.colorize(
                        "\n    => %d Errored\n" %
                        errored, 'red'))
            if todoed:
                self.stream.write(
                    util.colorize(
                        "\n    => %d ToDo  |" %
                        todoed, 'yellow'))
        else:
            self.stream.writeln("Tests End Succesfull...")
        return result


def main():
    suite = unittest.TestSuite()
    basedir = os.path.dirname(os.path.realpath(__file__))

    usage = "usage: %s [options] [tests to run]" % os.path.basename(
        sys.argv[0])
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Print detailed log.", default="False",
                        dest="verbose_print")
    options, args = parser.parse_known_args(args=sys.argv)

    if len(args) > 1:
        result = []
        for arg in args:
            realpath = os.path.realpath(arg)
            path = os.path.dirname(realpath)
            f = realpath[len(path) + 1:]

            if not f.startswith("test") or not f.endswith(".py"):
                raise Exception("Invalid argument: '%s'" % arg)

            mymodule = f[:-3]
            result.extend(getTests(path, basedir, [mymodule]))

        suite.addTests(result)
    else:
        testfile = '__test__.py'
        testDirs = []

        for root, dirs, files in os.walk(basedir):

            if testfile in files:
                testDirs.append(root)

        testDirs.sort()

        for mydir in testDirs:
            suite.addTests(getTests(os.path.join(basedir, mydir), basedir))

    verbosity = 1
    if options.verbose_print == True:
        verbosity = 2

    result = InaryTestRunner(
        verbosity=verbosity).run(
        suite, retresult=options.verbose_print)


def setup():
    options = inary.config.Options()
    options.destdir = 'tests/tmp_root'
    inary.api.set_options(options)

    ctx.config.values.general.distribution = "Sulin"
    ctx.config.values.general.distribution_release = "2018"


if __name__ == '__main__':
    if os.path.exists("tests/tmp_root"):
        shutil.rmtree("tests/tmp_root")
    setup()
    main()
