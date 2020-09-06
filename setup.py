#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2017, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import inary
import os
import shutil
import glob
import sys
import inspect
import tempfile
import subprocess
from distutils.core import setup
from distutils.cmd import Command
from distutils.command.build import build
from distutils.command.install import install
from distutils.sysconfig import get_python_lib

sys.path.insert(0, '.')

IN_FILES = ("inary.xml.in",)
PROJECT = "inary"
CONFIG_DIR = "/etc/inary"
MIMEFILE_DIR = "/usr/share/mime/packages"
TMPFILES_DIR = "/usr/lib/tmpfiles.d"

# config file
if os.path.isfile(".config"):
    cfg = open(".config", "r").readlines()


def getConfig(name=""):
    if not os.path.isfile(".config"):
        return True
    for line in cfg:
        if name in line:
            return "y" in line.split("=")[1]
    return False


class Build(build):
    def run(self):
        # Preparing configure file
        shutil.copy("config/inary.conf-{}".format(os.uname().machine),
                    "config/inary.conf")

        build.run(self)

        self.mkpath(self.build_base)
        if getConfig("NLS_SUPPORT"):
            for in_file in IN_FILES:
                name, ext = os.path.splitext(in_file)
                self.spawn(["intltool-merge", "-x", "po", in_file,
                            os.path.join(self.build_base, name)])


class BuildPo(build):
    def run(self):
        if getConfig("NLS_SUPPORT"):
            build.run(self)
            self.build_po()

    @staticmethod
    def build_po():
        import optparse
        files = tempfile.mkstemp()[1]
        filelist = []

        # Include optparse module path to translate
        optparse_path = os.path.abspath(optparse.__file__).rstrip("co")

        # Collect headers for mimetype files
        for filename in IN_FILES:
            os.system("intltool-extract --type=gettext/xml {}".format(filename))

        for root, dirs, filenames in os.walk("inary"):
            for filename in filenames:
                if filename.endswith(".py"):
                    filelist.append(os.path.join(root, filename))

        filelist.extend(["inary-cli", "inary.xml.in.h", optparse_path])
        filelist.sort()
        with open(files, "w") as _files:
            _files.write("\n".join(filelist))

        # Generate POT file
        os.system("xgettext -L Python \
                            --default-domain={0} \
                            --keyword=_ \
                            --keyword=N_ \
                            --files-from={1} \
                            -o po/{2}.pot".format(PROJECT, files, PROJECT))

        # Update PO files
        # FIXME: enable this block
        # for item in glob.glob1("po", "*.po"):
        #   print("Updating .. ", item)
        #   os.system("msgmerge --update --no-wrap --sort-by-file po/{0} po/{1}.pot".format(item, PROJECT))

        # Cleanup
        os.unlink(files)
        for f in filelist:
            if not f.endswith(".h"):
                continue
            try:
                os.unlink(f)
            except OSError:
                pass


class Install(install):
    def run(self):
        install.run(self)
        self.installi18n()
        self.generateConfigFile()

    def finalize_options(self):
        # NOTE: for Sulin distribution
        if os.path.exists("/etc/sulin-release"):
            self.install_platlib = '$base/lib/sulin'
            self.install_purelib = '$base/lib/sulin'
        install.finalize_options(self)

    def installi18n(self):
        if not getConfig("NLS_SUPPORT"):
            return
        for name in os.listdir('po'):
            if not name.endswith('.po'):
                continue
            lang = name[:-3]
            print("Installing '{}' translations...".format(lang))
            os.system("msgfmt po/{0}.po -o po/{0}.mo".format(lang))
            if not self.root:
                self.root = "/"
            destpath = os.path.join(
                self.root, "usr/share/locale/{}/LC_MESSAGES".format(lang))
            if not os.path.exists(destpath):
                os.makedirs(destpath)
            shutil.copy("po/{}.mo".format(lang),
                        os.path.join(destpath, "inary.mo"))

    def generateConfigFile(self):
        import inary.configfile
        destpath = os.path.join(self.root, CONFIG_DIR)
        if not os.path.exists(destpath):
            os.makedirs(destpath)

        confFile = os.path.join(destpath, "inary.conf")
        if os.path.isfile(confFile):  # Don't overwrite existing inary.conf
            return

        inaryconf = open(confFile, "w")

        klasses = inspect.getmembers(inary.configfile, inspect.isclass)
        defaults = [
            klass for klass in klasses if klass[0].endswith('Defaults')]

        for d in defaults:
            section_name = d[0][:-len('Defaults')].lower()
            inaryconf.write("[{}]\n".format(section_name))

            section_members = [m for m in inspect.getmembers(d[1])
                               if not m[0].startswith('__')
                               and not m[0].endswith('__')]

            for member in section_members:
                if member[1] is None or member[1] == "":
                    inaryconf.write("# {0[0]} = {0[1]}\n".format(member))
                else:
                    inaryconf.write("{0[0]} = {0[1]}\n".format(member))
            inaryconf.write('\n')


class Test(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.run_command('build')
        os.chdir('tests')
        subprocess.check_call([
            sys.executable, '-bWd',
            os.path.join('runTests.py')
        ])


setup(name="inary",
      version=inary.__version__,
      description="Inary (Special Package Manager)",
      long_description="Inary is the package management system of Sulin Linux.",
      license="GNU GPLv3",
      author="Zaryob",
      author_email="zaryob.dev@gmail.com",
      url="https://github.com/Zaryob/inary",
      # package_dir = {'': ''},

      packages=['inary',
                'inary.actionsapi',
                'inary.analyzer',
                'inary.cli',
                'inary.data',
                'inary.db',
                'inary.libraries',
                'inary.util',
                'inary.operations',
                'inary.sxml'],
      cmdclass={'build': Build,
                'build_po': BuildPo,
                'install': Install,
                'test': Test},
      data_files=[(CONFIG_DIR, ["config/inary.conf", "config/mirrors.conf"]),
                  (MIMEFILE_DIR, ["build/inary.xml"] if getConfig("NLS_SUPPORT") else [])],
      scripts=(['inary-cli',
                'scripts/pspec2po',
                'scripts/revdep-rebuild',
                'scripts/sulinstrapt',
                'scripts/makepkg',
                'scripts/makekagami',
                'scripts/mkdeb',
                'scripts/revdep-rebuild-devel',
                'scripts/inary-sandbox',
                'scripts/inarysh',
                'scripts/lsinary',
                'scripts/mkinary',
                'scripts/detect-dep',
                'scripts/detect-file-dep',
                'scripts/uninary',
                'scripts/genpspec',
                'scripts/update-inary-cache',
                'scripts/version-bump'] if getConfig("ADDITIONAL_SCRIPTS") else ['inary-cli']),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Environment :: Plugins',
          'Framework :: Sphinx',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
          'Natural Language :: English',
          'Natural Language :: Dutch',
          'Natural Language :: French',
          'Natural Language :: German',
          'Natural Language :: Hungarian',
          'Natural Language :: Italian',
          'Natural Language :: Portuguese (Brazilian)',
          'Natural Language :: Russian',
          'Natural Language :: Slovak',
          'Natural Language :: Turkish',
          'Natural Language :: Ukrainian',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Operating System :: POSIX :: BSD',
          'Programming Language :: Python :: 3 :: Only',
          'Topic :: Desktop Environment',
          'Topic :: System',
          'Topic :: System :: Installation/Setup',
          'Topic :: Software Development :: Bug Tracking',
      ],
      )

# the below stuff is really nice but we already have a version
# we can use this stuff for svn snapshots in a separate
# script, or with a parameter I don't know -- exa

INARY_VERSION = inary.__version__
