#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# pisi-key script adopted from apt-key
#
# Author : Serdar Dalgic - serdar AT pardus DOT org DOT tr
# Any comments are welcomed
#
# TODO:
# * a python wrapper for GPG can be used instead of using python's subprocess module
# * Fill in rest of the functions
# WARNING!! Still a prototype
#

import sys
import os
import subprocess

# We don't use a secret keyring, of course, but gpg panics and
# implodes if there isn't one available
GPG_CMD = 'gpg --ignore-time-conflict --no-options --no-default-keyring \
            --secret-keyring /etc/pisi/secring.gpg --trustdb-name /etc/pisi/trustdb.gpg'

GPG = GPG_CMD

MASTER_KEYRING = ''
ARCHIVE_KEYRING_URI = ''
# MASTER_KEYRING = '/usr/share/keyrings/pardus-master-keyring.gpg'
# ARCHIVE_KEYRING_URI = 'http://ftp.pardus.org.tr/pardus/pardus-archive-keyring.gpg'

ARCHIVE_KEYRING='/usr/share/keyrings/pardus-archive-keyring.gpg'
REMOVED_KEYS='/usr/share/keyrings/pardus-archive-removed-keys.gpg'

def addKey(GPG, keyfile):
    """ add the key """

    cmd = GPG + ' --quiet --batch --import %s' % keyfile
    print "cmd: " + cmd
    pass
    pipe = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return pipe.wait() == 0

def removeKey(GPG, keyfile):
    """ remove the key """

    cmd = GPG + ' --quiet --batch --delete-key --yes %s' % keyfile
    print "cmd: " + cmd
    pass
    pipe = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return pipe.wait() == 0

def update(GPG):
    """ update keys using the keyring package:

     we do not use add_keys_with_verify_against_master_keyring here,
     because "update" is run on regular package updates.  An
     attacker might as well replace the master-archive-keyring file
     in the package and add his own keys. so this check wouldn't
     add any security. we *need* this check on net-update though """

    if not os.access(ARCHIVE_KEYRING, os.F_OK):
        print "ERROR: Can't find the archive-keyring"
        print "Is the pisi-archive-keyring package installed?"
        sys.exit(1)

    cmd = GPG_CMD + ' --quiet --batch --keyring %s --export | %s --import' % (ARCHIVE_KEYRING, GPG)
    print "cmd: " + cmd
    pass
    pipe = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if not pipe.wait() == 0:
        print "An error occured, inform the maintainer about this issue"
        sys.exit(1)

    if os.access(REMOVED_KEYS, os.R_OK):
        # remove no-longer supported/used keys
        cmd = '%s --keyring %s --with-colons --list-keys | grep ^pub | cut -d: -f5' % (GPG_CMD, REMOVED_KEYS)
        pipe = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        keys = pipe.stdout.read()
        for key in keys:
            cmd = '%s --list-keys --with-colons | grep ^pub | cut -d: -f5 | grep -q %s' % (GPG, key)
            pipe = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if pipe.stdout.read():
                cmd = '%s --quiet --batch --delete-key --yes %s' % (GPG, key)
    else:
        print "Warning: removed keys keyring %s missing or not readable" % REMOVED_KEYS
        sys.exit(1)


def net_update():
    """ update the current archive signing keyring from a network URI:
    the archive-keyring keys needs to be signed with the master key
    (otherwise it does not make sense from a security POV) """
    if len(ARCHIVE_KEYRING_URI) == 0:
        print "Error: no location for the archive-keyring given"
        sys.exit(1)

    #TODO: Network connection should be checked!!
    if not os.path.isdir("/var/lib/pisi/keyrings"):
        os.mkdir("/var/lib/pisi/keyrings")

    keyring = "/var/lib/pisi/keyrings/%s" ARCHIVE_KEYRING.split("/")[-1]
    if os.path.exists(keyring):
        old_mtime = os.stat(keyring).st_mtime
    else:
        old_mtime = 0
    
    pass

def list_keys(GPG):
    """ list keys """
    cmd = GPG + ' --batch --list_keys'
    print "cmd: " + cmd
    pass
    pipe = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return pipe.wait() == 0

def list_fingerprints(GPG):
    """ list fingerprints """
    cmd = GPG + ' --batch --fingerprint'
    print "cmd: " + cmd
    pass
    pipe = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return pipe.wait() == 0

def export(GPG, keyid):
    """ output the key with the <keyid> """
    cmd = GPG + ' --armor --export %s' keyid
    print "cmd: " + cmd
    pass
    pipe = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return pipe.wait() == 0

def exportAll(GPG):
    """ output all trusted keys """
    cmd = GPG + ' --armor --export'
    print "cmd: " + cmd
    pipe = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return pipe.wait() == 0

def printUsage():
    """
        Prints usage information of application and exits.
    """

    print "Usage: pisi-key [--keyring file] [command] [arguments]"
    print
    print "Manage pisi's list of trusted keys"
    print
    print "  pisi-key add <file>          - add the key contained in <file> ('-' for stdin)"
    print "  pisi-key del <keyid>         - remove the key <keyid>"
    print "  pisi-key export <keyid>      - output the key <keyid>"
    print "  pisi-key exportall           - output all trusted keys"
    print "  pisi-key update              - update keys using the keyring package"
    print "  pisi-key net-update          - update keys using the network"
    print "  pisi-key list                - list keys"
    print "  pisi-key finger              - list fingerprints"
    print "  pisi-key adv                 - pass advanced options to gpg (download key)"
    print
    print "If no specific keyring file is given the command applies to all keyring files."
    sys.exit(1)

if __name__ == '__main__':

    if len(sys.argv) < 2:
        printUsage()
        sys.exit(1)

    argc=1
    #FIXME:: check whether gnupg is installed on the system or not!!

    # Determine on which keyring we want to work
    # if sys.argv[1] == '--keyring':
    if sys.argv[argc] == '--keyring':
        # keyring is the TRUSTEDFILE
        argc += 1 # becomes 2
        keyring = sys.argv[argc]
        if not os.access(keyring, F_OK):
            print "Error: The specified keyring %s is missing or not readable" % keyring
            sys.exit(1)

        argc += 1 # becomes 3
        operation = sys.argv[argc]
        GPG += ' --keyring %s --primary-keyring %s' % (keyring, keyring)
        argc += 1 # becomes 4

    else:
        # otherwise use the default
        keyring = '/etc/pisi/trusted.gpg'
        if os.access(keyring, os.F_OK):
            GPG += ' --keyring %s' % keyring
        GPG += ' --primary-keyring %s' % keyring
            #NOTICE:: TRUSTEDPARTS is not implemented.
        operation = sys.argv[argc]
        argc += 1 # becomes 2

    # print 'COMMAND: %s' % GPG

    if operation == 'help':
        printUsage()
        sys.exit(0)

    elif operation == 'add':
        keyfile = sys.argv[argc]
        # TODO: check whether key_path is alive ('-' can be used for stdin) e.g. gpg --keyring pisi-keyring.gpg --armour --export 102030AB | pisi-key add -
        addKey(GPG, keyfile)
        print "Key in %s is succesfully added." % keyfile

    elif operation == 'del':
        keyfile = sys.argv[argc]
        removeKey(GPG, keyfile)
        print "Key in %s is succesfully deleted." % keyfile

    elif operation == 'update':
        update(GPG)

    elif operation == 'net-update':
        net_update()

    elif operation == 'list':
        list_keys(GPG)

    elif operation == 'finger':
        list_fingerprints(GPG)

    elif operation == 'export':
        keyid = sys.argv[argc]
        export(GPG, keyid)

    elif operation == 'exportall':
        exportAll(GPG)

    elif operation == 'adv':
        adv_command = GPG + ' ' + sys.args[3:]
        print 'Executing: ' + adv_command
        # TODO: execute
        pass
    else:
        printUsage()

