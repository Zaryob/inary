# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
# This module is part of  inary.util

import inary.context as ctx

import os
import subprocess

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


##############################
# Process Releated Functions #
##############################

def search_executable(executable):
    """Search for the executable in user's paths and return it."""
    for _path in os.environ["PATH"].split(":"):
        full_path = os.path.join(_path, executable)
        if os.path.exists(full_path) and os.access(full_path, os.X_OK):
            return full_path
    return None

def run_batch(cmd, ui_debug=True):
    """Run command and report return value and output."""
    ctx.ui.info(_('Running ') + cmd, verbose=True)
    p = subprocess.Popen(cmd, shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if ui_debug: ctx.ui.debug(_('return value for "{0}" is {1}').format(cmd, p.returncode))
    return p.returncode, out, err

# TODO: it might be worthwhile to try to remove the
# use of ctx.stdout, and use run_batch()'s return
# values instead. but this is good enough :)
def run_logged(cmd):
    """Run command and get the return value."""
    ctx.ui.info(_('Running ') + cmd, verbose=True)
    if ctx.stdout:
        stdout = ctx.stdout
    else:
        if ctx.get_option('debug'):
            stdout = None
        else:
            stdout = subprocess.PIPE
    if ctx.stderr:
        stderr = ctx.stderr
    else:
        if ctx.get_option('debug'):
            stderr = None
        else:
            stderr = subprocess.STDOUT

    p = subprocess.Popen(cmd, shell=True, stdout=stdout, stderr=stderr)
    out, err = p.communicate()
    ctx.ui.debug(_('return value for "{0}" is {1}').format(cmd, p.returncode))

    return p.returncode

def get_cpu_count():
    """
    This function part of portage
    Copyright 2015 Gentoo Foundation
    Distributed under the terms of the GNU General Public License v2

    Using:
    Try to obtain the number of CPUs available.
    @return: Number of CPUs or None if unable to obtain.
    """
    try:
        import multiprocessing
        return multiprocessing.cpu_count()
    except (ImportError, NotImplementedError):
        return None

def get_kernel_option(option):
    """Get a dictionary of args for the given kernel command line option"""

    args = {}

    try:
        cmdline = open("/proc/cmdline").read().split()
    except IOError:
        return args

    for cmd in cmdline:
        if "=" in cmd:
            optName, optArgs = cmd.split("=", 1)
        else:
            optName = cmd
            optArgs = ""

        if optName == option:
            for arg in optArgs.split(","):
                if ":" in arg:
                    k, v = arg.split(":", 1)
                    args[k] = v
                else:
                    args[arg] = ""

    return args

def get_vm_info():
    vm_info = {}
    if platform.system() == 'Linux':
        try:
            proc = subprocess.Popen(["free"],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
        except OSError:
            pass
        output = proc.communicate()[0].decode('utf-8')
        if proc.wait() == os.EX_OK:
            for line in output.splitlines():
                line = line.split()
                if len(line) < 2:
                    continue
                if line[0] == "Mem:":
                    try:
                        vm_info["ram.total"] = int(line[1]) * 1024
                    except ValueError:
                        pass
                    if len(line) > 3:
                        try:
                            vm_info["ram.free"] = int(line[3]) * 1024
                        except ValueError:
                            pass
                elif line[0] == "Swap:":
                    try:
                        vm_info["swap.total"] = int(line[1]) * 1024
                    except ValueError:
                        pass
                    if len(line) > 3:
                        try:
                            vm_info["swap.free"] = int(line[3]) * 1024
                        except ValueError:
                            pass
    else:
        try:
            proc = subprocess.Popen(["sysctl", "-a"],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
        except OSError:
            pass
        else:
            output = proc.communicate()[0].decode('utf-8')
            if proc.wait() == os.EX_OK:
                for line in output.splitlines():
                    line = line.split(":", 1)
                    if len(line) != 2:
                        continue
