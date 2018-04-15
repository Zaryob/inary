# -*- coding: utf-8 -*-

import hashlib
import os
import sys
import time

import inary.db
import inary.operations

IGNORE_DIRS = ('/root',
               '/tmp',
               '/home',
               '/media',
               '/mnt',
               '/proc',
               '/sys',
               '/dev',
               '/var/run',
               '/var/inary',
               '/var/lib/inary',
               '/var/tmp',
               '/var/log',
               '/var/db/sudo',
               '/var/lock/subsys',
               '/var/spool',
               '/var/cache',
               '/var/db/comar3/scripts',
               '/var/db/comar3/apps',
               '/var/lib/mysql/mysql',
               '/etc/mudur/services')

IGNORE_EXTS = ('.pyc',
               '.pid')

def get_hash(filepath):
    def _hash(_str):
        return hashlib.sha1(_str.encode('utf-8')).hexdigest()

    if os.path.islink(filepath):
        data = os.path.realpath(filepath)
    else:
        data = open(filepath).read()

    return _hash(data)

def find_unowned(rootdir, last_unowned):
    db = inary.db.installdb.InstallDB()
    all_files = []
    for package in inary.db.installdb.InstallDB().list_installed():
        files = ['/' + x.path for x in db.get_files(package).list]
        all_files.extend(files)
    filepaths = []
    for root, dirs, files in os.walk(rootdir):
        if root in IGNORE_DIRS:
            while len(dirs):
                dirs.pop()
            continue
        for name in files:
            if name.endswith(IGNORE_EXTS):
                continue
            filepath = os.path.join(root, name)
            if filepath not in all_files and filepath not in last_unowned:
                sys.stdout.write("UNOWNED %s\n" % filepath)
                sys.stdout.flush()

def find_corrupted(rootdir, last_changed):
    for package in inary.db.installdb.InstallDB().list_installed():
        check = inary.operations.check.check_package(package, config=False)

        for filepath in check['corrupted']:
            filepath = '/' + filepath
            if not filepath.startswith(rootdir):
                continue
            if filepath not in last_changed or last_changed[filepath] != get_hash(filepath):
                sys.stdout.write("CHANGED %s %s %s\n" % (get_hash(filepath), package, filepath))
                sys.stdout.flush()

        for filepath in check['missing']:
            filepath = '/' + filepath
            if not filepath.startswith(rootdir):
                continue
            sys.stdout.write("MISSING {0} {1}\n".format(package, filepath))
            sys.stdout.flush()

def forensics(rootdir='/',logfile='logfile'):
    if not rootdir.endswith('/'):
        rootdir += '/'

    if logfile:
        pass
    else:
        logfile = None

    last_unowned = []
    last_changed = {}

    if logfile:
        for line in open(logfile):
            line = line.strip()
            if line.startswith("UNOWNED"):
                _type, _filepath = line.split(' ', 1)
                last_unowned.append(_filepath)
            elif line.startswith("CHANGED"):
                _type, _hash, _package,_filepath = line.split(' ', 3)
                last_changed[_filepath] = _hash

    find_unowned(rootdir, last_unowned)
    find_corrupted(rootdir, last_changed)
