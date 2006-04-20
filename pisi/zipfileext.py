# -*- coding: utf-8 -*-
#
# Copyright (C) 2006, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
# Authors:  Eray Ozkural <eray at pardus.org.tr>
#                Faik Uygur   <faik at pardus.org.tr>
#

"""Extends zipfile module with lzma and bzip2 support"""

# python standard library modules
import os
import struct
import time
import binascii

# we are really extending the zipfile module, not rewriting it.
from zipfile import *

try:
    import zlib
except ImportError:
    zlib = None
try:
    import bz2
except ImportError:
    bz2 = None
try:
    import pylzma
except ImportError:
    pylzma = None

ZIP_BZIP2 = 12
ZIP_LZMA_BOGUS = 255  # FIXME: we are going to add the official ID when PKWARE gives it to us, and keep this one for a while

compression_methods = [ZIP_STORED, ZIP_DEFLATED, ZIP_BZIP2, ZIP_LZMA_BOGUS]


class ZipFileEntry:
    """File-like object used to access entries in a ZipFile, we're using a factory 
    design pattern that's a little better than switch blocks thrown about"""
    
    def __init__(self, fp):
        self.fp = fp
        self.readBytes = 0
        self.returnedBytes = 0 #FIXME: we don't use studlyCaps in python
        self.finished = 0
        self.buffer = ""

    def tell(self):
        return self.returnedBytes

    def read(self, compress_size, n=None):
        """read the whole file, or n bytes and return the decompressed stuff
        does it in a buffered fashion"""
        self.length = compress_size
        if self.finished:
            return ""
        if n is None:
            compr_data = self.fp.read(self.length)
            data = self.decompress(compr_data)
            self.finished = 1
            self.returnedBytes += len(data)
            return data
        else:
            # FIXME: must always decompress in streaming mode, not just when n is given
            while len(self.buffer) < n:  
                compr_data = self.fp.read(min(n, 1024 * 8, self.length - self.readBytes))
                self.readBytes += len(compr_data)
                if not data:
                    result = self.buffer # + self.flush_decompressor()
                    self.finished = 1
                    self.buffer = ""
                    self.returnedBytes += len(result)
                    return result
                else:
                    self.buffer += self.decompress(data)
            result = self.buffer[:n]
            self.buffer = self.buffer[n:]
            self.returnedBytes += len(result)
            return result

    #TODO: use this instead of bulk compression
    def write(self, infile):
        self.CRC = 0
        self.file_size = 0
        self.compress_size = 0
        while 1:
            buf = infile.read(1024 * 8)
            if not buf:
                break
            self.file_size = self.file_size + len(buf)
            self.CRC = binascii.crc32(buf, self.CRC)
            if compressor:
                buf = self.compress(buf)
            self.compress_size = self.compress_size + len(buf)
            self.fp.write(buf)
        return self.compress_size
#            if cmpr:
  #              buf = cmpr.flush()
    #            compress_size = compress_size + len(buf)
      #          self.fp.write(buf)

    def close(self):
        self.finished = 1
        del self.fp


#TODO: test deflate and bzip2 support thoroughly
class DeflatedZipFileEntry(ZipFileEntry):
    """File-like object used to read a deflated entry in a ZipFile"""
    
    def __init__(self, fp):
        ZipFileEntry.__init__(self, fp)
        self.decomp = zlib.decompressobj(-15)
        self.compressor = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION,
                                                                   zlib.DEFLATED, -15)
        
    def decompress(self, compr_data):
        return self.decomp.decompress(compr_data) + self.decomp.decompress("Z") + self.decomp.flush()

    def compress(self, data):
        # big deal with flush....
        return self.compressor.compress(data)  + compressor.flush()

    def write(self, infile):
        data = infile.read()
        compressed = self.compress(data)
        self.fp.write(compressed)
        return len(compressed)


class Bzip2ZipFileEntry(ZipFileEntry):
    """File-like object used to read a BZIP2 entry in a ZipFile"""
    
    def __init__(self, fp):
        ZipFileEntry.__init__(self, fp)
        self.decomp = bz2.Decompressor()
        
    def decompress(self, compr_data):
        return self.decomp.decompress(compr_data)

    def write(self, infile):
        data = infile.read()
        self.file_size = len(data)
        self.CRC = binascii.crc32(data)
        compressed = bz2.compress(data)
        self.fp.write(compressed)
        self.compress_size = len(compressed)
        return self.compress_size


class LzmaZipFileEntry(ZipFileEntry):
    """File-like object used to read a LZMA entry in a ZipFile"""

    def __init__(self, fp):
        ZipFileEntry.__init__(self, fp)
        self.decompressor = pylzma.decompressobj()
    
    def decompress(self, compr_data):
        return self.decompressor.decompress(compr_data) + self.decompressor.flush()

    def write(self, infile):
        #TODO: use the buffered write in superclass
        data = infile.read()
        self.file_size = len(data)
        self.CRC = binascii.crc32(data)
        compressed = pylzma.compress(data, eos=1)
        self.fp.write(compressed)
        self.compress_size = len(compressed)
        return len(compressed)


class StoredZipFileEntry(ZipFileEntry):
    """File-like object used to read an uncompressed entry in a ZipFile"""
    
    def __init__(self, fp):
        ZipFileEntry.__init__(self, fp)
        
    def tell(self):
        return self.readBytes
    
    def read(self, length, n=None):
        self.length = length
        if n is None:
            n = self.length - self.readBytes
        if n == 0 or self.finished:
            return ''
        
        data = self.fp.read(n)
        self.readBytes += len(data)
        if self.readBytes == self.length or len(data) <  n:
            self.finished = 1
        return data

    def close(self):
        self.finished = 1
        del self.fp


class ZipFileExt(ZipFile):

    def build_file_entry(self, compress_type):
        "a small factory method"
        if compress_type == ZIP_STORED:
            return StoredZipFileEntry(self.fp)
        elif compress_type == ZIP_DEFLATED:
            if not zlib:
                raise RuntimeError, \
                      "Compression requires the missing %s module" % "zlib"
            return DeflatedZipFileEntry(self.fp)
        elif compress_type == ZIP_BZIP2:
            if not bz2:
                raise RuntimeError, \
                      "Compression method requires the missing %s module" % "bz2"
            return Bzip2ZipFileEntry(self.fp)
        elif compress_type == ZIP_LZMA_BOGUS:
            if not pylzma:
                raise RuntimeError, \
                      "Compression method requires the missing %s module" % "pylzma"
            return LzmaZipFileEntry(self.fp)
        else:
            raise BadZipfile, \
                  "Unsupported compression method %d for file %s" % \
            (compress_type, name)

    def _writecheck(self, zinfo):
        """Check for errors before writing a file to the archive."""
        if zinfo.filename in self.NameToInfo:
            if self.debug:      # Warning for duplicate names
                print "Duplicate name:", zinfo.filename
        if self.mode not in ("w", "a"):
            raise RuntimeError, 'write() requires mode "w" or "a"'
        if not self.fp:
            raise RuntimeError, \
                  "Attempt to write ZIP archive that was already closed"

    def write(self, filename, arcname=None, compress_type=ZIP_DEFLATED):
        """Put the bytes from filename into the archive under the name
        arcname."""
        st = os.stat(filename)
        mtime = time.localtime(st.st_mtime)
        date_time = mtime[0:6]
        # Create ZipInfo instance to store file information
        if arcname is None:
            zinfo = ZipInfo(filename, date_time)
        else:
            zinfo = ZipInfo(arcname, date_time)
        zinfo.external_attr = (st[0] & 0xFFFF) << 16L      # Unix attributes
        if compress_type is None:
            zinfo.compress_type = self.compression
        else:
            zinfo.compress_type = compress_type
        self._writecheck(zinfo)
        fp = open(filename, "rb")
        zinfo.flag_bits = 0x00
        zinfo.header_offset = self.fp.tell()    # Start of header bytes
        # Must overwrite CRC and sizes with correct data later
        zinfo.CRC = CRC = 0
        zinfo.compress_size = compress_size = 0
        zinfo.file_size = file_size = 0
        self.fp.write(zinfo.FileHeader())
        zinfo.file_offset = self.fp.tell()      # Start of file bytes

        # build a zipfileentry object from factory, and write compressed data
        fileentry = self.build_file_entry(zinfo.compress_type)
        fileentry.write(fp)
        # update zinfo
        zinfo.CRC = fileentry.CRC
        zinfo.file_size = fileentry.file_size
        zinfo.compress_size = fileentry.compress_size

        # Seek backwards and write CRC and file sizes
        position = self.fp.tell()       # Preserve current position in file
        self.fp.seek(zinfo.header_offset + 14, 0)
        self.fp.write(struct.pack("<lLL", zinfo.CRC, zinfo.compress_size,
                                                zinfo.file_size))
        self.fp.seek(position, 0)
        self.filelist.append(zinfo)
        self.NameToInfo[zinfo.filename] = zinfo

    def _readcheck(self, zinfo):
        """Return file-like object for name."""
        if self.mode not in ("r", "a"):
            raise RuntimeError, 'read() requires mode "r" or "a"'
        if not self.fp:
            raise RuntimeError, \
                  "Attempt to read ZIP archive that was already closed"
 
    def read(self, name):
        """Return file bytes (as a string) for name."""
        zinfo = self.getinfo(name)
        self._readcheck(zinfo)
        self.fp.seek(zinfo.file_offset, 0)
        f = self.build_file_entry(zinfo.compress_type)
        bytes = f.read(zinfo.compress_size)
        crc = binascii.crc32(bytes)
        if crc != zinfo.CRC:
            raise BadZipfile, "Bad CRC-32 for file %s" % name
        return bytes
