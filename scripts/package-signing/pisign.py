#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    PiSi Package Signing Tools
"""

import base64
import getpass
import os
import hashlib
import shlex
import subprocess
import sys
import tempfile
import zipfile

def sign_data(data, certificate, password_fd):
    """
        Signs data with given certificate.

        Arguments:
            data: Data to be signed
            certificate: Private certificate
            password_fd: File that contains passphrase
        Returns:
            Signed data
    """
    # Go to begining of password file
    password_fd.seek(0)

    # Use OpenSSL to sign data
    command = '/usr/bin/openssl dgst -sha1 -sign %s -passin fd:%d'
    command = command % (certificate, password_fd.fileno())
    command = shlex.split(command)

    pipe = subprocess.Popen(command, stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
    pipe.stdin.write(data)
    pipe.stdin.close()

    # Get signed data
    signed_binary = pipe.stdout.read()

    # Convert to Base 64
    signed_ascii = base64.b64encode(signed_binary)

    return signed_ascii

def verify_data(data, signature, key_file):
    """
        Verifies signature of data signed with given key file.

        Arguments:
            data: Original data
            signature_file: Signed data
            key_file: Public keyfile
        Returns:
            True if valid, False if invalid
    """
    # Keep signature in a temporary file
    signature_file = tempfile.NamedTemporaryFile()
    signature_file.write(signature)
    signature_file.flush()

    # Keep data in a temporary file
    data_file = tempfile.NamedTemporaryFile()
    data_file.write(data)
    data_file.flush()

    # Use OpenSSL to verify signature
    command = '/usr/bin/openssl dgst -sha1 -verify %s -signature %s %s'
    command = command % (key_file, signature_file.name, data_file.name)
    command = shlex.split(command)

    pipe = subprocess.Popen(command, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
    result = pipe.wait()

    # Destroy temporary files
    signature_file.close()
    data_file.close()

    return result == 0

def get_zip_hashes(zip_obj):
    """
        Calculates content hashes of a ZIP file.

        Example hash content:
            dir/file1 9971487c1c7ec8afbf4617460244ce4b9e11a867
            dir/file2 0b3e42702ef1c5190590534d0b3ee6c7fb45b0c6
            file3 7053bd69a3ba35cbcd2a635a090ec5f2cd439e29

        Arguments:
            zip_obj: ZipFile object
        Returns:
            ZIP content hashes
    """
    hashes = []

    for info in zip_obj.infolist():
        content = zip_obj.read(info.filename)
        content_hash = hashlib.sha1(content).hexdigest()
        hashes.append('%s %s' % (info.filename, content_hash))

    return "\n".join(hashes)

def verify_zipfile(filename, key_file):
    """
        Verifies integrity of a ZIP file.

        Arguments:
            filename: ZIP filename
            key_file: Public keyfile
        Returns:
            True if valid, False if invalid
    """

    try:
        zip_obj = zipfile.ZipFile(filename)
    except (IOError, zipfile.BadZipfile):
        return False

    # Get ZIP hashes
    hashes = get_zip_hashes(zip_obj)

    # Read signed hash data from ZIP comment
    signature = base64.b64decode(zip_obj.comment)

    # Close ZIP file
    zip_obj.close()

    # Verify signed data
    return verify_data(hashes, signature, key_file)

def sign_zipfile(filename, certificate, password_fd):
    """
        Signs ZIP file with given certificate.

        Arguments:
            filename: File name to be signed
            certificate: Private certificate
            password_fd: File that contains passphrase
    """
    zip_obj = zipfile.ZipFile(filename, 'a')

    # Get ZIP hashes and sign them
    hashes = get_zip_hashes(zip_obj)
    hashes_signed = sign_data(hashes, certificate, password_fd)

    # Add signed data as ZIP comment
    zip_obj.comment = hashes_signed

    # Mark file as modified and save it
    zip_obj._didModify = True
    zip_obj.close()

def print_usage():
    """
        Prints usage information of application and exits.
    """

    print "Usage:"
    print "  %s sign <path/to/private_key> <file.zip  ...>" % sys.argv[0]
    print "  %s verify <path/to/public_key> <file.zip ...>" % sys.argv[0]
    sys.exit(1)

def main():
    """
        Main
    """

    try:
        operation = sys.argv[1]
    except IndexError:
        print_usage()

    if operation == 'sign':
        try:
            key_file = sys.argv[2]
        except IndexError:
            print_usage()

        if len(sys.argv[3:]):
            # Keep password in a temporary file
            password = getpass.getpass()
            password_fd = os.tmpfile()
            password_fd.write(password)
            password_fd.flush()

            for filename in sys.argv[3:]:
                sign_zipfile(filename, key_file, password_fd)
                print "Signed %s with %s" % (filename, key_file)

            # Destroy temporary file
            password_fd.close()
        else:
            print_usage()

    elif operation == 'verify':
        try:
            key_file = sys.argv[2]
        except IndexError:
            print_usage()

        if len(sys.argv[3:]):
            for filename in sys.argv[3:]:
                if verify_zipfile(filename, key_file):
                    print "%s is valid." % filename
                else:
                    print "%s is corrupted." % filename
        else:
            print_usage()

    else:
        print_usage()

if __name__ == "__main__":
    sys.exit(main())
