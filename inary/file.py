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
#

"""
generic file abstraction that allows us to use URIs for everything
we support only the simple read case ATM
we are just encapsulating a common pattern in our program, nothing big.
like all inary classes, it has been programmed in a non-restrictive way
"""

# Standard Python Modules
import os
import lzma
import shutil

# INARY Modules
from inary.errors import Error
import inary.uri
import inary.util
import inary.fetcher
from inary.errors import AlreadyHaveException, NoSignatureFound, InvalidSignature
import inary.context as ctx

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class File:
    # Compression types
    COMPRESSION_TYPE_AUTO = 0
    COMPRESSION_TYPE_BZ2 = 1
    COMPRESSION_TYPE_XZ = 2

    (read, write) = list(range(2))  # modes
    (detached, whatelse) = list(range(2))

    __compressed_file_extensions = {".xz": COMPRESSION_TYPE_XZ,
                                    ".bz2": COMPRESSION_TYPE_BZ2}

    @staticmethod
    def make_uri(uri):
        """handle URI arg"""
        if isinstance(uri, str):
            uri = inary.uri.URI(uri)
        elif not isinstance(uri, inary.uri.URI):
            raise Error(_("uri must have type either URI or string."))
        return uri

    @staticmethod
    def choose_method(filename, compress):
        if compress == File.COMPRESSION_TYPE_AUTO:
            for ext, method in list(File.__compressed_file_extensions.items()):
                if filename.endswith(ext):
                    return method

            return None
        else:
            return compress

    @staticmethod
    def is_compressed(filename):
        return filename.endswith(tuple(File.__compressed_file_extensions))

    @staticmethod
    def decompress(localfile, compress):
        compress = File.choose_method(localfile, compress)
        if compress == File.COMPRESSION_TYPE_XZ:
            open(
                localfile[:-3], "w").write(lzma.LZMAFile(localfile).read().decode('utf-8'))
            localfile = localfile[:-3]
        elif compress == File.COMPRESSION_TYPE_BZ2:
            import bz2
            open(localfile[:-4], "w").write(bz2.BZ2File(localfile).read())
            localfile = localfile[:-4]
        return localfile

    @staticmethod
    def download(uri, transfer_dir="/tmp", sha1sum=False,
                 compress=None, sign=None, copylocal=False, pkgname=''):

        assert isinstance(uri, inary.uri.URI)

        inary.util.ensure_dirs(transfer_dir)

        # Check file integrity before saving?
        check_integrity = sha1sum or sign
        origfile = inary.util.join_path(transfer_dir, uri.filename())

        if sha1sum:
            sha1filename = File.download(
                inary.uri.URI(
                    uri.get_uri() +
                    '.sha1sum'),
                transfer_dir)

            sha1f = open(sha1filename)
            newsha1 = sha1f.read().split("\n")[0]

        if uri.is_remote_file() or copylocal:
            tmpfile = check_integrity and uri.filename() + ctx.const.temporary_suffix
            localfile = inary.util.join_path(
                transfer_dir, tmpfile or uri.filename())

            # TODO: code to use old .sha1sum file, is this a necessary optimization?
            # oldsha1fn = localfile + '.sha1sum'
            # if os.exists(oldsha1fn):
            # oldsha1 = file(oldsha1fn).readlines()[0]
            if sha1sum and os.path.exists(origfile):
                oldsha1 = inary.util.sha1_file(origfile)
                if newsha1 == oldsha1:
                    # early terminate, we already got it ;)
                    raise AlreadyHaveException(uri, origfile)

            if uri.is_remote_file():
                ctx.ui.info(
                    _("Fetching {}").format(
                        uri.get_uri()),
                    verbose=True)
                inary.fetcher.fetch_url(
                    uri, transfer_dir, ctx.ui.Progress, tmpfile, pkgname)
            else:
                # copy to transfer dir
                inary.fetcher.fetch_from_locale(
                    uri.get_uri(), transfer_dir, destfile=localfile)
        else:
            localfile = uri.get_uri()  # TODO: use a special function here?
            if localfile.startswith("file:///"):
                localfile = localfile[7:]

            if not os.path.exists(localfile):
                raise IOError(_("File \"{}\" not found.").format(localfile))
            if not os.access(localfile, os.W_OK):
                oldfn = localfile
                localfile = inary.util.join_path(
                    transfer_dir, os.path.basename(localfile))
                shutil.copy(oldfn, localfile)

        def clean_temporary():
            temp_files = []
            if sha1sum:
                temp_files.append(sha1filename)
            if check_integrity:
                temp_files.append(localfile)
            for filename in temp_files:
                try:
                    os.unlink(filename)
                except OSError:
                    pass

        if sha1sum:
            if inary.util.sha1_file(localfile) != newsha1:
                clean_temporary()
                raise Error(
                    _("File integrity of \"{}\" compromised.\n localfile:{}\n newsha1: {}").format(
                        uri, inary.util.sha1_file(localfile), newsha1))

        if check_integrity:
            shutil.move(localfile, origfile)
            localfile = origfile

        localfile = File.decompress(localfile, compress)

        return localfile

    def __init__(self, uri, mode, transfer_dir="/tmp",
                 sha1sum=False, compress=None, sign=None):
        """it is pointless to open a file without a URI and a mode"""

        self.transfer_dir = transfer_dir
        self.sha1sum = sha1sum
        self.compress = compress
        self.sign = sign

        uri = File.make_uri(uri)
        if mode == File.read or mode == File.write:
            self.mode = mode
        else:
            raise Error(_("File mode must be either File.read or File.write"))
        if uri.is_remote_file():
            if self.mode == File.read:
                localfile = File.download(
                    uri, transfer_dir, sha1sum, compress, sign)
            else:
                raise Error(_("Remote write not implemented."))
        else:
            localfile = uri.get_uri()
            if self.mode == File.read:
                localfile = File.decompress(localfile, self.compress)

        if self.mode == File.read:
            access = 'r'
        else:
            access = 'w'
        self.__file__ = open(localfile, access)
        self.localfile = localfile

    def local_file(self):
        """returns the underlying file object"""
        return self.__file__

    def close(self, delete_transfer=False):  # TODO: look this parameter
        """this method must be called at the end of operation"""
        self.__file__.close()
        if self.mode == File.write:
            compressed_files = []
            ctypes = self.compress or 0
            if ctypes & File.COMPRESSION_TYPE_XZ:
                compressed_file = self.localfile + ".xz"
                compressed_files.append(compressed_file)
                lzma_file = lzma.LZMAFile(compressed_file, "w")
                lzma_file.write(open(self.localfile, "rb").read())
                lzma_file.close()

            if ctypes & File.COMPRESSION_TYPE_BZ2:
                import bz2
                compressed_file = self.localfile + ".bz2"
                compressed_files.append(compressed_file)
                bz2.BZ2File(
                    compressed_file, "w").write(
                    open(
                        self.localfile).read())

            if self.sha1sum:
                sha1 = inary.util.sha1_file(self.localfile)
                cs = open(self.localfile + '.sha1sum', 'w')
                cs.write(sha1)
                cs.close()
                for compressed_file in compressed_files:
                    sha1 = inary.util.sha1_file(compressed_file)
                    cs = open(compressed_file + '.sha1sum', 'w')
                    cs.write(sha1)
                    cs.close()

            if self.sign == File.detached:
                if inary.util.run_batch(
                        'gpg --detach-sig ' + self.localfile)[0]:
                    raise Error(
                        _("ERROR: \'gpg --detach-sig {}\' failed.").format(self.localfile))
                for compressed_file in compressed_files:
                    if inary.util.run_batch(
                            'gpg --detach-sig ' + compressed_file)[0]:
                        raise Error(
                            _("ERROR: \'gpg --detach-sig {}\' failed.").format(compressed_file))

    @staticmethod
    def check_signature(uri, transfer_dir, sign=detached):
        if sign == File.detached:
            try:
                sigfilename = File.download(
                    inary.uri.URI(uri + '.sig'), transfer_dir)
            except KeyboardInterrupt:
                raise
            except IOError:  # FIXME: what exception could we catch here, replace with that.
                ctx.ui.warning(NoSignatureFound(uri))
                return True

            result = inary.util.run_batch('gpg --verify ' + sigfilename)
            if ctx.config.values.general.ssl_verify and result[0]:
                ctx.ui.info(
                    "Checking GPG Signature failed ('gpg --verify {}')".format(
                        sigfilename),
                    color='cyan')
                ctx.ui.info(result[2].decode("utf-8"), color='faintcyan')
                if not ctx.ui.confirm(
                        "Would you like to skip checking gpg signature?"):
                    raise InvalidSignature(uri)  # everything is all right here
        else:
            return True

    def flush(self):
        self.__file__.flush()

    def fileno(self):
        return self.__file__.fileno()

    def isatty(self):
        return self.__file__.isatty()

    def __next__(self):
        return next(self.__file__)

    def read(self, size=None):
        if size:
            return self.__file__.read(size)
        else:
            return self.__file__.read()

    def readline(self, size=None):
        if size:
            return self.__file__.readline(size)
        else:
            return self.__file__.readline()

    def readlines(self, size=None):
        if size:
            return self.__file__.readlines(size)
        else:
            return self.__file__.readlines()

    def xreadlines(self):
        return self.__file__

    def seek(self, offset, whence=0):
        self.__file__.seek(offset, whence)

    def tell(self):
        return self.__file__.tell()

    def truncate(self):
        self.__file__.truncate()

    def write(self, str):
        self.__file__.write(str)

    def writelines(self, sequence):
        self.__file__.writelines(sequence)
