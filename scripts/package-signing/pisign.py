#!/usr/bin/python
# -*- coding: utf-8 -*-


import base64
import hashlib
import subprocess
import sys
import zipfile


def signData(data, keyfile, passphrase):
    """
        Signs data with given key file and passphrase.

        Arguments:
            data: Data to sign
            keyfile: Private key
            passphrase: Passphrase
        Returns:
            Signed data
    """

    cmd = '/usr/bin/openssl dgst -sha1 -sign %s -passin pass:%s' % (keyfile, passphrase)
    pipe = subprocess.Popen(cmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pipe.stdin.write(data)
    pipe.stdin.close()
    return pipe.stdout.read()


def verifyData(data, signature, keyfile=None, certificate=None):
    """
        Verifies signature. Keyfile or certificate is required.

        Arguments:
            data: Original data
            signature: Signed data
            keyfile: Public keyfile
            certificate: Certificate
        Returns:
            True if valid, False if invalid
    """

    if certificate:
        cmd = '/usr/bin/openssl x509 -inform pem -in %s -pubkey -noout' % certificate
        pipe = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        keyfile = '.tmp_key'
        # TODO: This is a workaround, fix ASAP
        file(keyfile, 'w').write(pipe.stdout.read())
    elif not keyfile:
        return False

    # TODO: This is a workaround, fix ASAP
    file('.tmp_data', 'w').write(data)
    file('.tmp_signature', 'w').write(signature)

    cmd = '/usr/bin/openssl dgst -sha1 -verify %s -signature .tmp_signature .tmp_data' % keyfile
    pipe = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return pipe.wait() == 0

def getZipSums(zip):
    """
        Calculates checksums of files in ZIP object.

        Arguments:
            zip: ZipFile object
        Returns:
            File names and sums
    """

    data = []
    for content in zip.infolist():
        content_sum = hashlib.sha1(zip.read(content.filename)).hexdigest()
        data.append('%s %s' % (content.filename, content_sum))
    return '\n'.join(data)


def verifyFile(filename, keyfile=None, certificate=None):
    """
        Verifies integrity of a ZIP file. Keyfile or certificate is required.

        Arguments:
            filename: ZIP filename
            keyfile: Public keyfile
            certificate: Certificate
        Returns:
            True if valid, False if invalid
    """

    try:
        zip = zipfile.ZipFile(filename)
    except IOError:
        return False
    sums = getZipSums(zip)
    signature = base64.b64decode(zip.comment)
    return verifyData(sums, signature, keyfile, certificate)


def signFile(filename, keyfile, passphrase):
    """
        Signs a ZIP file.

        Arguments:
            filename: ZIP filename
            keyfile: Private key
            passphrase: Passphrase
    """

    zip = zipfile.ZipFile(filename, 'a')
    # Sign file checksums
    sums = getZipSums(zip)
    signature = signData(sums, keyfile, passphrase)
    # Write Base64 encoded signature to ZIP file as comment
    zip.comment = base64.b64encode(signature)
    # Mark file as modified and save it
    zip._didModify = True
    zip.close()


def printUsage():
    """
        Prints usage information of application and exits.
    """

    print 'Usage:'
    print '  %s sign <path/to/zipfile> <path/to/private_key> <passphrase>' % sys.argv[0]
    print '  %s verify <path/to/zipfile> <path/to/certificate>' % sys.argv[0]
    sys.exit(1)


if __name__ == '__main__':

    try:
        operation, filename = sys.argv[1:3]
    except ValueError:
        printUsage()

    if operation == 'sign':
        try:
            keyfile, passphrase = sys.argv[3:5]
        except ValueError:
            printUsage()

        signFile(filename, keyfile, passphrase)

    elif operation == 'verify':
        try:
            certificate = sys.argv[3]
        except ValueError:
            printUsage()

        if verifyFile(filename, certificate=certificate):
            print 'File is OK'
        else:
            print 'File is corrupt'

    else:
        printUsage()
