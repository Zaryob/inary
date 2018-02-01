# -*- coding: utf-8 -*-
#
# Copyright (C) 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

"""sysutils module provides basic system utilities."""

import os
import time
import fcntl
import platform


class FileLock:
    def __init__(self, filename):
        self.filename = filename
        self.fd = None

    def lock(self, shared=False, timeout=-1):
        _type = fcntl.LOCK_EX
        if shared:
            _type = fcntl.LOCK_SH
        if timeout != -1:
            _type |= fcntl.LOCK_NB

        self.fd = os.open(self.filename, os.O_WRONLY | os.O_CREAT, 0o600)
        if self.fd == -1:
            raise IOError("Cannot create lock file")

        while True:
            try:
                fcntl.flock(self.fd, _type)
                return
            except IOError:
                if timeout > 0:
                    time.sleep(0.2)
                    timeout -= 0.2
                else:
                    raise

    def unlock(self):
        fcntl.flock(self.fd, fcntl.LOCK_UN)

def find_executable(exec_name):
    """find the given executable in PATH"""

    # preppend /bin, /sbin explicitly to handle system configuration
    # errors
    paths = ["/bin", "/sbin"]

    paths.extend(os.getenv("PATH").split(':'))

    for p in paths:
        exec_path = os.path.join(p, exec_name)
        if os.path.exists(exec_path):
            return exec_path

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

def get_vm_info():
    vm_info = {}

    try:
        import subprocess
    except ImportError:
        raise Exception(_("Module: \"subprocess\" can not import"))

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
