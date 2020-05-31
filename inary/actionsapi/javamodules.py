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

# Standard Python Modules
import os
from glob import glob
from shutil import copy, copytree

# Inary Modules
import inary.context as ctx
import inary.util as util

# ActionsAPI Modules
import inary.actionsapi
from inary.actionsapi.shelltools import system, export
from inary.actionsapi import get

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


# java -Xmx256M -jar x.jar --key=val
EXEC_TEMPLATE = """\
#!/bin/sh

cd {0}
java{1}-jar {2}{3}
"""


class CompileError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[JavaTools]: " + value)


class InstallError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[JavaTools]: " + value)


class RunTimeError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[JavaTools]: " + value)


class DoJavadocError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[JavaTools]: " + value)


####################
# Internal helpers #
####################


def _dodoc(*source_files, **kw):
    """copy doc files to /usr/share/doc/src_name recursively"""

    dest = util.join_path(get.docDIR(), kw.get('dest_dir', get.srcNAME()))
    destination = util.join_path(get.installDIR(), dest)

    if not os.access(destination, os.F_OK):
        os.makedirs(destination)

    for source_file in source_files:
        sources = glob(source_file)
        if not sources:
            raise DoJavadocError(
                _('No any file/directory matched to regex expression "{}".'.format(source_file)))

        for source in sources:
            if os.path.isfile(source):
                try:
                    copy(source, destination)
                except IOError:
                    raise DoJavadocError(_('DoJavadoc failed.'))
            elif os.path.isdir(source):
                target = util.join_path(destination, source.split("/")[-1])
                try:
                    copytree(source, target)
                except IOError:
                    raise DoJavadocError(_('DoJavadoc failed.'))


def _generate_classpath_file(classpath):
    """write classpath to environment file"""

    env_dir = util.join_path(get.installDIR(), '/etc/env.d')
    if not os.access(env_dir, os.F_OK):
        os.makedirs(env_dir)

    env_file = util.join_path(env_dir, get.srcNAME())
    if not os.access(env_file, os.F_OK):
        prefix = 'CLASSPATH='
    else:
        prefix = ':'

    cp_file = open(env_file, 'a')
    cp_file.write('{0}{1}'.format(prefix, ':'.join(classpath)))
    cp_file.close()


def _generate_exec_file(dest_dir, exe, java_args, exe_args):
    """generate executable file for executable jar"""

    exec_dir = util.join_path(get.installDIR(), '/usr/bin')
    if not os.access(exec_dir, os.F_OK):
        os.makedirs(exec_dir)

    # Using low level I/O to set permission without calling os.chmod
    exec_file = os.open(util.join_path(exec_dir, get.srcNAME()),
                        os.O_CREAT | os.O_WRONLY,
                        0o755)
    os.write(exec_file, EXEC_TEMPLATE.format(util.join_path('/', dest_dir),
                                             java_args,
                                             exe,
                                             exe_args))
    os.close(exec_file)


#############################
# Building and installation #
#############################


def compile(argument='', parameters='', build_tool='ant'):
    """compile source with given build tool and related parameters"""

    try:
        run(argument, parameters, build_tool)
    except RunTimeError:
        raise CompileError(_('Compile failed.'))


def installExe(exe='', java_args='', exe_args='', dest_dir=''):
    """install executable jar to specified location and get jar prepared to
    execute with given arguments.

    exe:        Path in work dir to executable jar
    java_args:  Arguments passed to jvm
    exe_args:   Arguments passed to executable jar
    dest_dir:   Installation dir of executable jar"""

    if not dest_dir:
        dest_dir = 'usr/share/java/{}'.format(get.srcNAME())
    destination = util.join_path(get.installDIR(), dest_dir)

    if not os.access(destination, os.F_OK):
        os.makedirs(destination)

    # To guarantee x/y.jar going under /usr/share/java as y.jar
    source = exe.split("/")[-1]
    try:
        copy(exe, destination)
        _generate_exec_file(dest_dir,
                            source,
                            ' {} '.format(java_args) if java_args else ' ',
                            ' {}'.format(exe_args) if exe_args else '')
    except IOError:
        raise InstallError(_('Installing file "{}" failed.'.format(exe)))


def installLib(src='*.jar', dest='/usr/share/java'):
    """install compilation output that is mix of the utility classes as
    in jars or meta/data files to specified locations.

    src:    Source file pattern to be installed
    dest:   Destination dir where the source files to be installed
    """

    classpath = []

    destination = util.join_path(get.installDIR(), dest)
    sources = glob(src)

    # If no source matched, then no need to create destination dir
    if not sources:
        raise InstallError(_('No any file/directory matched '
                             'to regex expression "{}".'.format(src)))

    if not os.access(destination, os.F_OK):
        os.makedirs(destination)

    for source in sources:
        if os.path.isfile(source):
            try:
                copy(source, destination)
            except IOError:
                raise InstallError(
                    _('Installing file "{}" failed.'.format(source)))
            if source.endswith('.jar'):
                classpath.append(util.join_path('/',
                                                dest,
                                                source.split('/')[-1]))
        elif os.path.isdir(source):
            target = util.join_path(destination, source.split('/')[-1])
            try:
                copytree(source, target)
            except IOError:
                raise InstallError(
                    _('Installing directory "{}" failed.'.format(source)))
            for root, dirs, files in os.walk(target):
                for f in files:
                    if f.endswith('.jar'):
                        # Exclude sandbox dir from jar path
                        jar = util.remove_prefix(get.installDIR(),
                                                 util.join_path(root, f))
                        classpath.append(jar)

    if classpath:
        _generate_classpath_file(classpath)


######################
# Javadoc generation #
######################


def dojavadoc(*source_files, **kw):
    """generate & copy javadoc files to /usr/share/doc/src_name recursively"""

    build_tool = kw.get('build_tool', 'ant')
    parameters = kw.get('parameters', '')
    argument = kw.get('argument', 'javadoc')

    try:
        run(argument, parameters, build_tool)
        _dodoc(*source_files, **kw)
    except (RunTimeError, DoJavadocError):
        raise DoJavadocError(_('Javadoc generation failed.'))


#####################
# Generic execution #
#####################


def run(argument='', parameters='', build_tool='ant'):
    """run build tool with given parameters"""

    export('JAVA_HOME', '/opt/sun-jre')
    # Otherwise, javadoc might be completed with errors
    export('LC_ALL', 'en_US.UTF-8')

    if system('{0} {1} {2}'.format(build_tool, parameters, argument)):
        raise RunTimeError(_('Run failed.'))
