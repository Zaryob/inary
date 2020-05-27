#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Inary Package Signing Tools
"""

import base64
import getpass
import io
import os
import hashlib
import shlex
import shutil
import subprocess
import sys
import tempfile
import zipfile

# ZipFile extensions
ZIP_FILES = ('.zip', '.inary')

# Signature headers & extensions
HEADER = 'inary-signed'
EXT_SIGN = 'sig'
EXT_CERT = 'crt'

# Signature validity
SIGN_OK, SIGN_NO, SIGN_SELF, SIGN_UNTRUSTED, SIGN_CORRUPTED = list(range(5))

# Certificate validity
CERT_OK, CERT_SELF, CERT_CORRUPTED = list(range(3))

# Certificate trustworthiness
CERT_TRUSTED, CERT_UNTRUSTED = list(range(2))


def sign_data(data, key_file, password_fd):
    """
        Signs data with given key.

        Arguments:
            data: Data to be signed
            key_file: Private key
            password_fd: File that contains passphrase
        Returns:
            Signed data (binary)
    """
    # Go to begining of password file
    password_fd.seek(0)
    # Use OpenSSL to sign data
    command = '/usr/bin/openssl dgst -sha1 -sign {} -passin file:{}'
    command = command.format(key_file, password_fd.name)

    command = shlex.split(command)

    pipe = subprocess.Popen(command, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    pipe.stdin.write(data.encode("utf-8"))
    pipe.stdin.close()
    # Get signed data
    signed_binary = pipe.stdout.read()
    print(pipe.stderr.read())
    return signed_binary


def get_public_key(cert_file):
    """
        Extracts public key from certificate.

        Arguments:
            cert_file: Certificate
        Returns:
            Public key
    """
    # Use OpenSSL to extract public key
    command = 'openssl x509 -inform pem -in {} -pubkey -noout'
    command = command.format(cert_file)
    command = shlex.split(command)

    pipe = subprocess.Popen(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    key_ascii = pipe.stdout.read()

    return key_ascii


def get_hash(cert_file):
    """
        Extracts hash from certificate.

        Arguments:
            cert_file: Certificate
        Returns:
            Hash
    """
    # Use OpenSSL to extract hash
    command = 'openssl x509 -noout -in {} -hash'
    command = command.format(cert_file)
    command = shlex.split(command)

    pipe = subprocess.Popen(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    hash = pipe.stdout.read()
    hash = hash.strip()

    return hash


def check_trust(cert_file, trust_dir):
    """
        Checks if certificate is trusted or not.

        Arguments:
            cert_file: Certificate
            trust_dir: Path to trust database.
        Returns:
            CERT_TRUSTED or CERT_UNTRUSTED
    """

    cert_hash = get_hash(cert_file)

    for filename in os.listdir(trust_dir):
        cert_path = os.path.join(trust_dir, filename)
        if os.path.exists(cert_path):
            if cert_hash == get_hash(cert_path):
                return CERT_TRUSTED
    return CERT_UNTRUSTED

    """
    # Code to be used in production:
    cert_hash = get_hash(cert_file)
    cert_path = os.path.join(trust_dir, cert_hash)
    if os.path.exists(cert_path):
        if cert_hash == get_hash(cert_path):
            return CERT_TRUSTED
    return CERT_UNTRUSTED
    """


def verify_certificate(cert_file):
    """
        Verifies a certificate.

        Arguments:
            cert_file: Certificate
        Returns:
            CERT_OK, CERT_SELF or CERT_CORRUPTED
    """
    # Use OpenSSL to verify certificate
    command = '/usr/bin/openssl verify {}'
    command = command.format(cert_file)
    command = shlex.split(command)

    pipe = subprocess.Popen(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    lines = pipe.stdout.read().decode("utf-8").split('\n')

    if len(lines) < 2:
        return CERT_CORRUPTED
    elif lines[1].startswith("error"):
        code = lines[1].split()[1]
        if code == '18':
            return CERT_SELF
        else:
            return CERT_CORRUPTED
    else:
        return CERT_OK


def verify_file(data_file, cert_file=None,
                signature_file=None, trust_dir=None):
    """
        Verifies signature of file signed with given certificate.

        If signature_file is not defined data_file + ".sig" will
        be used.

        If cert_file is not defined data_file + ".crt" will
        be used.

        Arguments:
            data_file: Original data file
            cert_file: Certificate (or None)
            signature_file: Signature file (or None)
            trust_dir: Path to trust database.
        Returns:
            SIGN_OK, SIGN_NO, SIGN_SELF or SIGN_CORRUPTED
    """
    # Sanitize before appending signature extension
    data_file = os.path.realpath(data_file)

    if not signature_file:
        signature_file = data_file + '.' + EXT_SIGN
    if not cert_file:
        cert_file = data_file + '.' + EXT_CERT
    if not os.path.exists(signature_file) or not os.path.exists(cert_file):
        return SIGN_NO

    # Verify certificate
    cert_validity = verify_certificate(cert_file)
    if cert_validity == CERT_CORRUPTED:
        return SIGN_CORRUPTED

    # Check trustworthiness of certificate
    if trust_dir is not None and check_trust(
            cert_file, trust_dir) == CERT_UNTRUSTED:
        return SIGN_UNTRUSTED

    # Keep public key in a temporary file
    pub_file = tempfile.NamedTemporaryFile()
    pub_file.write(get_public_key(cert_file))
    pub_file.flush()

    # Use OpenSSL to verify signature
    command = '/usr/bin/openssl dgst -sha1 -verify {} -signature {} {}'
    command = command.format(pub_file.name, signature_file, data_file)
    command = shlex.split(command)

    pipe = subprocess.Popen(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    result = pipe.wait()
    # Destroy temporary files
    pub_file.close()

    if result == 0:
        if cert_validity == CERT_OK:
            return SIGN_OK
        else:
            return SIGN_SELF
    else:
        return SIGN_CORRUPTED


def verify_data(data, signature_data, trust_dir):
    """
        Verifies signature of data signed with given certificate.

        Arguments:
            data: Original data
            signature_data: Signature data from ZipFile
            trust_dir: Path to trust database.
        Returns:
            SIGN_OK, SIGN_NO, SIGN_SELF or SIGN_CORRUPTED
    """
    # Check header
    if isinstance(type(signature_data), type(bytes)):
        signature_data = signature_data.decode("utf-8")
    if not len(signature_data) or not signature_data.startswith(HEADER):
        return SIGN_NO
    else:
        try:
            header, cert_ascii, signature_ascii = signature_data.split(':')
        except ValueError:
            return SIGN_CORRUPTED
        if header != HEADER:
            return SIGN_CORRUPTED
        signature_binary = base64.b64decode(signature_ascii)
        cert_data = base64.b64decode(cert_ascii)

    # Keep certificate in a temporary file
    cert_file = tempfile.NamedTemporaryFile()
    cert_file.write(cert_data)
    cert_file.flush()

    # Keep signature in a temporary file
    signature_file = tempfile.NamedTemporaryFile()
    signature_file.write(signature_binary)
    signature_file.flush()

    # Keep data in a temporary file
    data_file = tempfile.NamedTemporaryFile()
    data_file.write(data.encode("utf-8"))
    data_file.flush()

    # Verify
    result = verify_file(
        data_file.name,
        cert_file.name,
        signature_file.name,
        trust_dir)

    # Destroy temporary files
    cert_file.close()
    signature_file.close()
    data_file.close()

    return result


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
        hashes.append('{} {}'.format(info.filename, content_hash))

    return "\n".join(hashes)


def verify_zipfile(filename, trust_dir=None):
    """
        Verifies integrity of a ZIP file.

        Arguments:
            filename: ZIP filename
            trust_dir: Path to trust database.
        Returns:
            SIGNED, UNSIGNED, SELF_SIGNED or CORRUPTED
    """

    try:
        zip_obj = zipfile.ZipFile(filename)
    except (IOError, zipfile.BadZipfile):
        return False

    # Get ZIP hashes
    hashes = get_zip_hashes(zip_obj)

    # Read signed hash data from ZIP comment
    signature_data = zip_obj.comment

    # Close ZIP file
    zip_obj.close()

    # Verify signed data
    return verify_data(hashes, signature_data, trust_dir)


def sign_file(filename, key_file, cert_file, password_fd):
    """
        Signs file with given key.

        Arguments:
            filename: File name to be signed
            key_file: Private key
            cert_file: Certificate
            password_fd: File that contains passphrase
    """
    data = open(filename).read()
    signed_binary = sign_data(data, key_file, password_fd)
    cert_data = open(cert_file, "rb").read()

    # Save certificate
    open('{}.{}'.format(filename, EXT_CERT), 'wb').write(cert_data)

    # Save signed data
    open('{}.{}'.format(filename, EXT_SIGN), 'wb').write(signed_binary)


def sign_zipfile(filename, key_file, cert_file, password_fd):
    """
        Signs ZIP file with given key.

        Arguments:
            filename: File name to be signed
            key_file: Private key
            cert_file: Certificate
            password_fd: File that contains passphrase
    """
    zip_obj = zipfile.ZipFile(filename, 'a')

    # Get ZIP hashes and sign them
    hashes = get_zip_hashes(zip_obj)
    signed_binary = sign_data(hashes, key_file, password_fd)
    signed_ascii = base64.b64encode(signed_binary)

    # Encode certificate
    cert_data = open(cert_file, "rb").read()
    cert_ascii = base64.b64encode(cert_data)

    # Add signed data as ZIP comment
    zip_obj.comment = HEADER.encode(
        "utf-8") + b":" + cert_ascii + b":" + signed_ascii

    # Mark file as modified and save it
    zip_obj._didModify = True
    zip_obj.close()


def print_usage():
    """
        Prints usage information of application and exits.
    """

    print("Usage:")
    print("  {} sign <priv_key> <cert> <file1 ...>".format(sys.argv[0]))
    print("  {} verify <trust_dir> <file1 ...>".format(sys.argv[0]))
    print("  {} generate_certs <cert_dir> <trusted ...>".format(sys.argv[0]))
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
            cert_file = sys.argv[3]
        except IndexError:
            print_usage()

        if len(sys.argv[4:]):
            # Keep password in a temporary file
            password = getpass.getpass()
            temporary_name = tempfile.mkstemp()[1]

            with open(temporary_name, mode="a+") as password_fd:
                password_fd.write(password)
                password_fd.flush()

                for filename in sys.argv[4:]:
                    if filename.endswith(ZIP_FILES):
                        sign_zipfile(
                            filename, key_file, cert_file, password_fd)
                    else:
                        sign_file(filename, key_file, cert_file, password_fd)
                    print("Signed {} with {}".format(filename, key_file))

                os.remove(temporary_name)

        else:
            print_usage()

    elif operation == 'verify':
        try:
            trust_dir = sys.argv[2]
        except IndexError:
            print_usage()

        if len(sys.argv[3:]):
            for filename in sys.argv[3:]:
                if filename.endswith(ZIP_FILES):
                    result = verify_zipfile(filename, trust_dir)
                else:
                    result = verify_file(filename, trust_dir=trust_dir)
                if result == SIGN_OK:
                    print("{} is signed by a trusted source.".format(filename))
                elif result == SIGN_NO:
                    print("{} is unsigned.".format(filename))
                elif result == SIGN_SELF:
                    print(
                        "{} is self-signed by a trusted source.".format(filename))
                elif result == SIGN_UNTRUSTED:
                    print(
                        "{} is signed by an untrusted source.".format(filename))
                else:
                    print("{} is corrupted.".format(filename))
        else:
            print_usage()
    elif operation == 'generate_certs':
        if len(sys.argv[3:]):
            print("Generating certificates...")
            print("Creating certificate directory: {}".format(sys.argv[2]))
            if not os.path.exists(sys.argv[2]):
                os.makedirs(sys.argv[2])
            print(
                "Creating trusted certificate directory: {}".format(
                    sys.argv[3]))
            if not os.path.exists(sys.argv[3]):
                os.makedirs(sys.argv[3])

            temporary_name = tempfile.mkstemp()[1]

            with open(temporary_name, mode="a+") as password_fd:
                password = getpass.getpass()
                password_fd.write(password)
                password_fd.flush()

                os.system(
                    "/usr/bin/openssl genrsa -des3 -out {0}/enc_key.pem 1024".format(sys.argv[2]))

                os.system(
                    "/usr/bin/openssl req -new -subj '/C=TR/ST=Sivas/L=Merkez/CN=Sulin' -key {0}/enc_key.pem -out {0}/req.pem -passin file:{1}".format(
                        sys.argv[2],
                        temporary_name))
                os.system(
                    "/usr/bin/openssl req -x509 -key {0}/enc_key.pem -in {0}/req.pem -out {0}/cert.pem -days 365 -passin file:{1}".format(
                        sys.argv[2], temporary_name))
                shutil.copy("{}/cert.pem".format(sys.argv[2]), sys.argv[3])
                os.remove(temporary_name)
        else:
            print_usage()

    else:
        print_usage()


if __name__ == "__main__":
    sys.exit(main())
