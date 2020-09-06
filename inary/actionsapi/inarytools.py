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

"""supports globs in sourceFile arguments"""

# Standart Python Modules
import filecmp
import fileinput
import glob
import os
import re
import sys

# Inary Modules
from inary.util.files import uncompress
from inary.util.strings import remove_prefix
from inary.errors import FileError, Error

# ActionsAPI Modules
import inary.actionsapi
from inary.actionsapi import error
from inary.actionsapi.shelltools import *
import inary.actionsapi.get as get

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


# Tool functions
def executable_insinto(destinationDirectory, *sourceFiles):
    """insert a executable file into destinationDirectory"""

    if not sourceFiles or not destinationDirectory:
        raise ArgumentError(_('Insufficient arguments.'))

    if not can_access_directory(destinationDirectory):
        makedirs(destinationDirectory)

    for sourceFile in sourceFiles:
        sourceFileGlob = glob.glob(sourceFile)
        if len(sourceFileGlob) == 0:
            raise FileError(
                _("No executable file matched pattern \"{}\".").format(sourceFile))

        for source in sourceFileGlob:
            # FIXME: use an internal install routine for these
            system(
                'install -m 0755 -o root -g root {0} {1}'.format(source, destinationDirectory))


def readable_insinto(destinationDirectory, *sourceFiles):
    """inserts file list into destinationDirectory"""

    if not sourceFiles or not destinationDirectory:
        raise ArgumentError(_('Insufficient arguments.'))

    if not can_access_directory(destinationDirectory):
        makedirs(destinationDirectory)

    for sourceFile in sourceFiles:
        sourceFileGlob = glob.glob(sourceFile)
        if len(sourceFileGlob) == 0:
            raise FileError(
                _("No file matched pattern \"{}\".").format(sourceFile))

        for source in sourceFileGlob:
            system(
                'install -m 0644 "{0}" {1}'.format(source, destinationDirectory))


def lib_insinto(sourceFile, destinationDirectory, permission=644):
    """inserts a library fileinto destinationDirectory with given permission"""

    if not sourceFile or not destinationDirectory:
        raise ArgumentError(_('Insufficient arguments.'))

    if not can_access_directory(destinationDirectory):
        makedirs(destinationDirectory)

    if os.path.islink(sourceFile):
        os.symlink(
            os.path.realpath(sourceFile),
            os.path.join(
                destinationDirectory,
                sourceFile))
    else:
        system('install -m 0{0} {1} {2}'.format(permission,
                                                sourceFile, destinationDirectory))


# inarytools funtions
def dobin(sourceFile, destinationDirectory='/usr/bin'):
    """insert a executable file into /bin or /usr/bin"""
    ''' example call: inarytools.dobin("bin/xloadimage", "/bin", "xload") '''
    executable_insinto(
        join_path(
            get.installDIR(),
            destinationDirectory),
        sourceFile)


def dopixmaps(sourceFile, destinationDirectory='/usr/share/pixmaps'):
    """insert a data file into /usr/share/pixmaps"""
    ''' example call: inarytools.dopixmaps("/usr/share/pixmaps/firefox", "firefox") '''
    readable_insinto(
        join_path(
            get.installDIR(),
            destinationDirectory),
        sourceFile)


def dodir(destinationDirectory):
    """creates a directory tree"""
    makedirs(join_path(get.installDIR(), destinationDirectory))


def dodoc(*sourceFiles, **kw):
    """inserts the files in the list of files into /usr/share/doc/PACKAGE"""
    destDir = kw.get("destDir", get.srcNAME())
    readable_insinto(
        join_path(
            get.installDIR(),
            get.docDIR(),
            destDir),
        *sourceFiles)


def dohtml(*sourceFiles, **kw):
    """inserts the files in the list of files into /usr/share/doc/PACKAGE/html"""

    ''' example call: inarytools.dohtml("doc/doxygen/html/*")'''
    destDir = kw.get("destDir", get.srcNAME())
    destionationDirectory = join_path(
        get.installDIR(), get.docDIR(), destDir, 'html')

    if not can_access_directory(destionationDirectory):
        makedirs(destionationDirectory)

    allowed_extensions = [
        '.png',
        '.gif',
        '.html',
        '.htm',
        '.jpg',
        '.css',
        '.js']
    disallowed_directories = ['CVS', '.git', '.svn', '.hg']

    for sourceFile in sourceFiles:
        sourceFileGlob = glob.glob(sourceFile)
        if len(sourceFileGlob) == 0:
            raise FileError(
                _("No file matched pattern \"{}\".").format(sourceFile))

        for source in sourceFileGlob:
            if os.path.isfile(source) and os.path.splitext(
                    source)[1] in allowed_extensions:
                system(
                    'install -m 0644 "{0}" {1}'.format(source, destionationDirectory))
            if os.path.isdir(source) and os.path.basename(
                    source) not in disallowed_directories:
                eraser = os.path.split(source)[0]
                for root, dirs, files in os.walk(source):
                    newRoot = remove_prefix(eraser, root)
                    for sourcename in files:
                        if os.path.splitext(sourcename)[
                                1] in allowed_extensions:
                            makedirs(join_path(destionationDirectory, newRoot))
                            system('install -m 0644 {0} {1}'.format(join_path(root, sourcename),
                                                                    join_path(destionationDirectory, newRoot,
                                                                              sourcename)))


def doinfo(*sourceFiles):
    """inserts the into files in the list of files into /usr/share/info"""
    readable_insinto(join_path(get.installDIR(), get.infoDIR()), *sourceFiles)


def dolib(sourceFile, destinationDirectory='/usr/lib', mode=755):
    """insert the library into /usr/lib"""
    '''example call: inarytools.dolib("libz.a")'''
    '''example call: inarytools.dolib("libz.so")'''
    if mode == 755 and sourceFile.endswith('.a'):
        mode = 644
    sourceFile = join_path(os.getcwd(), sourceFile)
    destinationDirectory = join_path(get.installDIR(), destinationDirectory)

    lib_insinto(sourceFile, destinationDirectory, mode)


def doman(*sourceFiles, pageDirectory=None):
    """inserts the man pages in the list of files into /usr/share/man/"""

    '''example call: inarytools.doman("man.1", "sulin.*")'''
    manDIR = join_path(get.installDIR(), get.manDIR())
    if not can_access_directory(manDIR):
        makedirs(manDIR)

    for sourceFile in sourceFiles:
        sourceFileGlob = glob.glob(sourceFile)
        if len(sourceFileGlob) == 0:
            raise FileError(
                _("No file matched pattern \"{}\"").format(sourceFile))

        for source in sourceFileGlob:
            compressed = source.endswith("gz") and source
            if compressed:
                source = source[:-3]
            try:
                if not pageDirectory:
                    pageDirectory = source[source.rindex('.') + 1:]
            except ValueError:
                error(
                    _('ActionsAPI [doman]: Wrong man page file: \"{}\"').format(source))

            manPDIR = join_path(manDIR, '/man{}'.format(pageDirectory))
            makedirs(manPDIR)
            if not compressed:
                system('install -m 0644 {0} {1}'.format(source, manPDIR))
            else:
                uncompress(compressed, targetDir=manPDIR)


def domo(sourceFile, locale, destinationFile,
         localeDirPrefix='/usr/share/locale'):
    """inserts the mo files in the list of files into /usr/share/locale/LOCALE/LC_MESSAGES"""

    '''example call: inarytools.domo("po/tr.po", "tr", "pam_login.mo")'''

    system('msgfmt {}'.format(sourceFile))
    makedirs('{0}{1}/{2}/LC_MESSAGES/'.format(get.installDIR(),
                                              localeDirPrefix, locale))
    move('messages.mo',
         '{0}{1}/{2}/LC_MESSAGES/{3}'.format(get.installDIR(),
                                             localeDirPrefix,
                                             locale,
                                             destinationFile))


def domove(sourceFile, destination, destinationFile=''):
    """moves sourceFile/Directory into destinationFile/Directory"""

    ''' example call: inarytools.domove("/usr/bin/bash", "/bin/bash")'''
    ''' example call: inarytools.domove("/usr/bin/", "/usr/sbin")'''
    makedirs(join_path(get.installDIR(), destination))

    sourceFileGlob = glob.glob(join_path(get.installDIR(), sourceFile))
    if len(sourceFileGlob) == 0:
        raise FileError(
            _("No file matched pattern \"{}\". 'domove' operation failed.").format(sourceFile))

    for filePath in sourceFileGlob:
        if not destinationFile:
            move(
                filePath,
                join_path(
                    get.installDIR(),
                    join_path(
                        destination,
                        os.path.basename(filePath))))
        else:
            move(
                filePath,
                join_path(
                    get.installDIR(),
                    join_path(
                        destination,
                        destinationFile)))


def rename(sourceFile, destinationFile):
    """ renames sourceFile as destinationFile"""

    ''' example call: inarytools.rename("/usr/bin/bash", "bash.old") '''
    ''' the result of the previous example would be "/usr/bin/bash.old" '''

    baseDir = os.path.dirname(sourceFile)

    try:
        os.rename(
            join_path(
                get.installDIR(),
                sourceFile),
            join_path(
                get.installDIR(),
                baseDir,
                destinationFile))
    except OSError as e:
        error(_('ActionsAPI [rename]: \"{0}\": \"{1}\"').format(e, sourceFile))


def dosed(sources, findPattern, replacePattern='',
          filePattern='', deleteLine=False, level=-1):
    """replaces patterns in sources"""

    ''' example call: inarytools.dosed("/etc/passwd", "caglar", "cem")'''
    ''' example call: inarytools.dosed("/etc/passwd", "caglar")'''
    ''' example call: inarytools.dosed("/etc/pass*", "caglar")'''
    ''' example call: inarytools.dosed("Makefile", "(?m)^(HAVE_PAM=.*)no", r"\1yes")'''
    ''' example call: inarytools.dosed("./", "^(CFLAGS) =", r"\1 +=", "Makefile", level = 1)
        will change: ./Makefile and ./*/Makefile'''
    ''' example call: inarytools.dosed("./", "^\s*g_type_init\(\)", filePattern = ".*.c", deleteLine = True)
        will change: delete lines which contains "g_type_init()" for all *.c files in ./ directory tree'''

    def get_files(path, pattern, level):
        res = []
        if path.endswith("/"):
            path = path[:-1]
        for root, dirs, files in os.walk(path):
            currentLevel = len(root.split("/")) - len(path.split("/"))
            if not level == -1 and currentLevel > level:
                continue
            for f in files:
                if re.search(pattern, f):
                    res.append("{0}/{1}".format(root, f))
        return res

    backupExtension = ".inary-backup"
    sourceFiles = []
    sourcesGlob = glob.glob(sources)

    for source in sourcesGlob:
        if os.path.isdir(source):
            sourceFiles.extend(get_files(source, filePattern, level))
        else:
            sourceFiles.append(source)

    # if there is no match, raise exception
    if len(sourceFiles) == 0:
        raise FileError(_('No such file matching pattern: \"{}\". \'dosed\' operation failed.').format(
            filePattern if filePattern else sources))

    for sourceFile in sourceFiles:
        if can_access_file(sourceFile):
            backupFile = "{0}{1}".format(sourceFile, backupExtension)
            for line in fileinput.input(
                    sourceFile, inplace=1, backup=backupExtension):
                # FIXME: In-place filtering is disabled when standard input is
                # read
                if re.search(findPattern, line):
                    line = "" if deleteLine else re.sub(
                        findPattern, replacePattern, line)
                sys.stdout.write(line)
            if can_access_file(backupFile):
                # By default, filecmp.cmp() compares two files by looking file sizes.
                # shallow=False tells cmp() to look file content.
                if filecmp.cmp(sourceFile, backupFile, shallow=False):
                    ctx.ui.warning(
                        _('dosed method has not changed file \"{}\".').format(sourceFile))
                else:
                    ctx.ui.info(
                        _("\"{}\" has been changed by dosed method.").format(
                            sourceFile),
                        verbose=True)
                os.unlink(backupFile)
        else:
            raise FileError(
                _('File does not exist or permission denied: \"{}\"').format(sourceFile))


def dosbin(sourceFile, destinationDirectory='/usr/sbin'):
    """insert a executable file into /sbin or /usr/sbin"""

    ''' example call: inarytools.dobin("bin/xloadimage", "/sbin") '''
    executable_insinto(
        join_path(
            get.installDIR(),
            destinationDirectory),
        sourceFile)


def dosym(sourceFile, destinationFile):
    """creates soft link between sourceFile and destinationFile"""

    ''' example call: inarytools.dosym("/usr/bin/bash", "/bin/bash")'''
    makedirs(join_path(get.installDIR(), os.path.dirname(destinationFile)))

    try:
        os.symlink(sourceFile, join_path(get.installDIR(), destinationFile))
    except OSError:
        error(_('ActionsAPI [dosym]: File already exists: \"{}\"').format(
            destinationFile))


def insinto(destinationDirectory, sourceFile, destinationFile='', sym=True):
    """insert a sourceFile into destinationDirectory as a destinationFile with same uid/guid/permissions"""
    makedirs(join_path(get.installDIR(), destinationDirectory))

    if not destinationFile:
        sourceFileGlob = glob.glob(sourceFile)
        if len(sourceFileGlob) == 0:
            raise FileError(
                _("No file matched pattern \"{}\".").format(sourceFile))

        for filePath in sourceFileGlob:
            if can_access_file(filePath):
                copy(filePath, join_path(get.installDIR(), join_path(destinationDirectory, os.path.basename(filePath))),
                     sym)
    else:
        copy(
            sourceFile,
            join_path(
                get.installDIR(),
                join_path(
                    destinationDirectory,
                    destinationFile)),
            sym)


def newdoc(sourceFile, destinationFile):
    """inserts a sourceFile into /usr/share/doc/PACKAGE/ directory as a destinationFile"""
    destinationDirectory = os.path.dirname(destinationFile)
    destinationFile = os.path.basename(destinationFile)
    # Use copy instead of move or let build-install scream like file not found!
    copy(sourceFile, destinationFile)
    readable_insinto(
        join_path(
            get.installDIR(),
            'usr/share/doc',
            get.srcNAME(),
            destinationDirectory),
        destinationFile)


def newman(sourceFile, destinationFile):
    """inserts a sourceFile into /usr/share/man/manPREFIX/ directory as a destinationFile"""
    # Use copy instead of move or let build-install scream like file not found!
    copy(sourceFile, destinationFile)
    doman(destinationFile)


def remove(sourceFile):
    """removes sourceFile"""
    sourceFileGlob = glob.glob(join_path(get.installDIR(), sourceFile))
    if len(sourceFileGlob) == 0:
        raise FileError(
            _("No file matched pattern \"{}\". Remove operation failed.").format(sourceFile))

    for filePath in sourceFileGlob:
        unlink(filePath)


def removeDir(destinationDirectory):
    """removes destinationDirectory and its subtrees"""
    destdirGlob = glob.glob(join_path(get.installDIR(), destinationDirectory))
    if len(destdirGlob) == 0:
        raise FileError(
            _("No directory matched pattern \"{}\". Remove directory operation failed.").format(destinationDirectory))

    for directory in destdirGlob:
        unlinkDir(directory)


class Flags:
    def __init__(self, *evars):
        self.evars = evars

    def add(self, *flags):
        for evar in self.evars:
            os.environ[evar] = " ".join(
                os.environ[evar].split() + [f.strip() for f in flags])

    def remove(self, *flags):
        for evar in self.evars:
            os.environ[evar] = " ".join(
                [v for v in os.environ[evar].split() if v not in [f.strip() for f in flags]])

    def replace(self, old_val, new_val):
        for evar in self.evars:
            os.environ[evar] = " ".join(
                [new_val if v == old_val else v for v in os.environ[evar].split()])

    def sub(self, pattern, repl, count=0, flags=0):
        for evar in self.evars:
            os.environ[evar] = re.sub(
                pattern, repl, os.environ[evar], count, flags)

    def reset(self):
        for evar in self.evars:
            os.environ[evar] = ""


cflags = Flags("CFLAGS")
ldflags = Flags("LDFLAGS")
cxxflags = Flags("CXXFLAGS")
flags = Flags("CFLAGS", "CXXFLAGS")
