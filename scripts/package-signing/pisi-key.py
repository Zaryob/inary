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
import subprocess

# We don't use a secret keyring, of course, but gpg panics and
# implodes if there isn't one available
GPG = 'gpg --ignore-time-conflict --no-options --no-default-keyring \
        --secret-keyring /etc/pisi/secring.gpg --trustdb-name /etc/pisi/trustdb.gpg'

MASTER_KEYRING = ''
ARCHIVE_KEYRING_URI = ''
# MASTER_KEYRING = '/usr/share/keyrings/pardus-master-keyring.gpg'
# ARCHIVE_KEYRING_URI = 'http://ftp.pardus.org.tr/pardus/pardus-archive-keyring.gpg'

ARCHIVE_KEYRING=/usr/share/keyrings/pardus-archive-keyring.gpg
REMOVED_KEYS=/usr/share/keyrings/pardus-archive-removed-keys.gpg

def addKey(GPGcommand, keyfile):
    cmd = GPGcommand + ' --quiet --batch --import %s' % keyfile
    pipe = subprocess.call(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return pipe.wait() == 0

def removeKey():
    pass

def update():
    pass

def net_update():
    pass

def list_keys():
    pass

def list_fingerprints():
    pass

def export():
    pass

def exportAll():
    pass

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
        #FIXME:: check whether keyrings are accessible
        argc += 1 # becomes 2
        keyring = sys.argv[argc]
        argc += 1 # becomes 3
        operation = sys.argv[argc]
        argc += 1 # becomes 4
    elif:
        # otherwise use the default
        keyring = '/etc/pisi/trusted.gpg'
        operation = sys.argv[argc]
        argc += 1 # becomes 2

    GPG += ' --keyring %s --primary-keyring %s' % (keyring, keyring)

    #TRUSTEDPARTS is not implemented.

    if operation == 'add':
        # add the key
        keyfile = sys.argv[argc]
        # check whether key_path is alive ('-' can be used for stdin)
        addKey(GPG, keyfile)

    elif operation == 'del':
        # remove the key
        removeKey()

    elif operation == 'update':
        # update keys using the keyring package
        update()

    elif operation == 'net-update':
        # update keys using the network
        net_update()

    elif operation == 'list':
        # list keys
        GPG += ' --batch --list-keys'
        list_keys()

    elif operation == 'finger':
        # list fingerprints
        GPG += ' --batch --fingerprint'
        list_fingerprints()

    elif operation == 'export':
        # output the key with the <keyid>
        keyid = sys.argv[argc]
        argc += 1 #increment argc
        GPG += ' --armor --export %s' % keyid
        export()

    elif operation == 'exportall':
        # output all trusted keys
        GPG += ' --armor --export'
        exportAll()

    elif operation == 'adv':
        adv_command = GPG + ' ' + sys.args[3:]
        print 'Executing: ' + adv_command
        # TODO: execute
        pass
    else:
        printUsage()
        sys.exit(1)


