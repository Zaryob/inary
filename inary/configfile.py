# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2020, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# INARY Configuration File module, obviously, is used to read from the
# configuration file. Module also defines default values for
# configuration parameters.
#
# Configuration file is located in /etc/inary/inary.conf by default,
# having an INI like format like below.
#
# [general]
# destinationdirectory = /
# autoclean = False
# bandwidth_limit = 0
#
# [build]
# host = i686-pc-linux-gnu
# generateDebug = False
# jobs = "-j3"
# CFLAGS= -mtune=generic -march=i686 -O2 -pipe -fomit-frame-pointer -fstack-protector -D_FORTIFY_SOURCE=2
# CXXFLAGS= -mtune=generic -march=i686 -O2 -pipe -fomit-frame-pointer -fstack-protector -D_FORTIFY_SOURCE=2
# LDFLAGS= -Wl,-O1 -Wl,-z,relro -Wl,--hash-style=gnu -Wl,--as-needed -Wl,--sort-common
# buildhelper = None / ccache / icecream
# compressionlevel = 1
# fallback = "ftp://ftp.pardus.org.tr/pub/source/2009"
#
# [directories]
# lib_dir = /var/lib/inary
# info_dir = "/var/lib/inary/info"
# history_dir = /var/lib/inary/history
# archives_dir = /var/cache/inary/archives
# cached_packages_dir = /var/cache/inary/packages
# compiled_packages_dir = "/var/cache/inary/packages"
# index_dir = /var/cache/inary/index
# packages_dir = /var/cache/inary/package
# tmp_dir = /var/inary
# kde_dir = /usr/kde/4
# qt_dir = /usr/qt/4
# kde5_dir =
# qt5_dir =

# Standard Python Modules
import io
import os
import re
import configparser

# INARY Modules
import inary.errors

# Öşex like this
from inary.util import hewal as eval

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class Error(inary.errors.Error):
    pass


class GeneralDefaults:
    """Default values for [general] section"""
    destinationdirectory = "/"
    autoclean = False
    distribution = "Sulin"
    distribution_release = "2019"
    distribution_id = "s19"
    architecture = "x86_64"
    allowrfp = False
    http_proxy = os.getenv("HTTP_PROXY") or None
    https_proxy = os.getenv("HTTPS_PROXY") or None
    ftp_proxy = os.getenv("FTP_PROXY") or None
    package_cache = False
    package_cache_limit = 0
    ssl_verify = True
    bandwidth_limit = 0
    no_color = False
    ignore_safety = False
    ignore_delta = False

    # SELECT FETCHER DOWNLOAD BACKEND
    # 0 - Auto (try and choose)
    #     pyCurl -> requests -> wget
    # 1 - Force pyCurl
    # 2 - Force requests
    # 3 - Force wget (on shell)
    #
    # Note: if you entered invalid number to here,
    #       using default one
    fetcher_mode = 0

    # FETCHER USER-AGENT STRING
    fetcher_useragent = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'

    # FETCHER CHUNK SIZE
    fetcher_chunksize = 8196


class BuildDefaults:
    """Default values for [build] section"""
    build_host = "localhost"
    host = "x86_64-linux-gnu"
    jobs = "-j1"
    generateDebug = True
    cflags = "-mtune=generic -O2 -pipe -fomit-frame-pointer -fstack-protector -D_FORTIFY_SOURCE=2"
    cxxflags = "-mtune=generic -O2 -pipe -fomit-frame-pointer -fstack-protector -D_FORTIFY_SOURCE=2"
    ldflags = "-Wl,-O1 -Wl,-z,relro -Wl,--hash-style=gnu -Wl,--as-needed -Wl,--sort-common"
    makeflags = ""
    allow_docs = True
    allow_pages = True
    allow_dbginfo = True
    allow_static = True
    buildhelper = None
    compressionlevel = 9
    fallback = "http://www.sulin.com.tr/pub"
    ignored_build_types = ""


class DirectoriesDefaults:
    """Default values for [directories] section"""
    lib_dir = "/var/lib/inary"
    log_dir = "/var/log"
    info_dir = "/var/lib/inary/info"
    history_dir = "/var/lib/inary/history"
    archives_dir = "/var/cache/inary/archives"
    cache_root_dir = "/var/cache/inary"
    cached_packages_dir = "/var/cache/inary/packages"
    compiled_packages_dir = "/var/cache/inary/packages"
    debug_packages_dir = "/var/cache/inary/packages-debug"
    old_paths_cache_dir = "/var/cache/inary/old-paths"
    packages_dir = "/var/lib/inary/package"
    lock_dir = "/var/lock/subsys"
    index_dir = "/var/lib/inary/index"
    tmp_dir = "/var/inary"
    kde_dir = "/usr/kde/5"
    qt_dir = "/usr/qt/5"


class ConfigurationSection(object):
    """ConfigurationSection class defines a section in the configuration
        file, using defaults (above) as a fallback."""

    def __init__(self, section, items=None):
        if items is None:
            items = []
        self.items = items

        if section == "general":
            self.defaults = GeneralDefaults
        elif section == "build":
            self.defaults = BuildDefaults
        elif section == "directories":
            self.defaults = DirectoriesDefaults
        else:
            e = _("No section by name '{}'").format(section)
            raise Error(e)

        self.section = section

    def __getattr__(self, attr):

        # first search for attribute in the items provided in the
        # configuration file.
        if self.items:
            for item in self.items:
                if item[0] == attr:
                    # all values are returned as string types by ConfigParser.
                    # evaluate "True" or "False" strings to boolean.
                    if item[1] in ["True", "False", "None"]:
                        return eval(item[1])
                    else:
                        return item[1]

        # then fall back to defaults
        if hasattr(self.defaults, attr):
            return getattr(self.defaults, attr)

        return ""

    # We'll need to access configuration keys by their names as a
    # string. Like; ["default"]...
    def __getitem__(self, key):
        return self.__getattr__(key)


class ConfigurationFile(object):
    """Parse and get configuration values from the configuration file"""

    def __init__(self, filePath):
        self.parser = configparser.ConfigParser()
        self.filePath = filePath

        self.parser.read(self.filePath)

        try:
            generalitems = self.parser.items("general")
        except configparser.NoSectionError:
            generalitems = []
        self.general = ConfigurationSection("general", generalitems)

        try:
            builditems = self.parser.items("build")
        except configparser.NoSectionError:
            builditems = []
        self.build = ConfigurationSection("build", builditems)

        try:
            dirsitems = self.parser.items("directories")
        except configparser.NoSectionError:
            dirsitems = []
        self.dirs = ConfigurationSection("directories", dirsitems)

        try:
            directiveitems = self.parser.items("directives")
        except configparser.NoSectionError:
            self.directives = {}
        else:
            self.directives = {}
            for k, v in directiveitems:
                if v in ("True", "False"):
                    self.directives[k] = eval(v)
                else:
                    self.directives[k] = v

    # get, set and write_config methods added for manipulation of inary.conf file from Scom to solve bug #5668.
    # Current ConfigParser does not keep the comments and white spaces, which we do not want for inary.conf. There
    # are patches floating in the python sourceforge to add this feature. The write_config code is from python
    # sourceforge tracker id: #1410680, modified a little to make it turn into
    # a function.

    def get(self, section, option):
        try:
            return self.parser.get(section, option)
        except configparser.NoOptionError:
            return None

    def set(self, section, option, value):
        self.parser.set(section, option, value)

    def write_config(self, add_missing=True):
        sections = {}
        current = io.StringIO()
        replacement = [current]
        sect = None
        opt = None
        written = []
        optcre = re.compile(
            r'(?P<option>[^:=\s][^:=]*)'
            r'(?P<vi>[:=])'
            r'(?P<padding>\s*)'
            r'(?P<value>.*)$'
        )

        fp = open(self.filePath, "r+")
        # Default to " = " to match write(), but use the most recent
        # separator found if the file has any options.
        padded_vi = " = "
        while True:
            line = fp.readline()
            if not line:
                break
            # Comment or blank line?
            if line.strip() == '' or line[0] in '#;' or \
                    (line.split(None, 1)[0].lower() == 'rem' and
                     line[0] in "rR"):
                current.write(line)
                continue
            # Continuation line?
            if line[0].isspace() and sect is not None and opt:
                if ';' in line:
                    # ';' is a comment delimiter only if it follows
                    # a spacing character
                    pos = line.find(';')
                    if line[pos - 1].isspace():
                        comment = line[pos - 1:]
                        # Get rid of the newline, and put in the comment.
                        current.seek(-1, 1)
                        current.write(comment + "\n")
                continue
            # A section header or option header?
            else:
                # Is it a section header?
                mo = self.parser.SECTCRE.match(line)
                if mo:
                    # Remember the most recent section with this name,
                    # so that any missing options can be added to it.
                    if sect:
                        sections[sect] = current
                    sect = mo.group('header')
                    current = io.StringIO()
                    replacement.append(current)
                    sects = self.parser.sections()
                    sects.append(configparser.DEFAULTSECT)
                    if sect in sects:
                        current.write(line)
                    # So sections can't start with a continuation line:
                    opt = None
                # An option line?
                else:
                    mo = optcre.match(line)
                    if mo:
                        padded_opt, vi, value = mo.group('option', 'vi',
                                                         'value')
                        padded_vi = ''.join(mo.group('vi', 'padding'))
                        comment = ""
                        if vi in ('=', ':') and ';' in value:
                            # ';' is a comment delimiter only if it follows
                            # a spacing character
                            pos = value.find(';')
                            if value[pos - 1].isspace():
                                comment = value[pos - 1:]
                        # Keep track of what we rstrip to preserve formatting
                        opt = padded_opt.rstrip().lower()
                        padded_vi = padded_opt[len(opt):] + padded_vi
                        if self.parser.has_option(sect, opt):
                            value = self.parser.get(sect, opt)
                            # Fix continuations.
                            value = value.replace("\n", "\n\t")
                            current.write("{0}{1}{2}{3}\n".format(opt, padded_vi,
                                                                  value, comment))
                            written.append((sect, opt))
        if sect:
            sections[sect] = current
        if add_missing:
            # Add any new sections.
            sects = self.parser.sections()
            if len(self.parser._defaults) > 0:
                sects.append(configparser.DEFAULTSECT)
            sects.sort()
            for sect in sects:
                if sect == configparser.DEFAULTSECT:
                    opts = list(self.parser._defaults.keys())
                else:
                    # Must use _section here to avoid defaults.
                    opts = list(self.parser._sections[sect].keys())
                opts.sort()
                if sect in sections:
                    output = sections[sect] or current
                else:
                    output = current
                    if len(written) > 0:
                        output.write("\n")
                    output.write("[{}]\n".format(sect))
                    sections[sect] = None
                for opt in opts:
                    if opt != "__name__" and not (sect, opt) in written:
                        value = self.parser.get(sect, opt)
                        # Fix continuations.
                        value = value.replace("\n", "\n\t")
                        output.write(
                            "{0}{1}{2}\n".format(
                                opt, padded_vi, value))
                        written.append((sect, opt))
        # Copy across the new file.
        fp.seek(0)
        fp.truncate()
        for sect in replacement:
            if sect is not None:
                fp.write(sect.getvalue())

        fp.close()
