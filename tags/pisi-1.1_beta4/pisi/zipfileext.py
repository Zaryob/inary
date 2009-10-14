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
# Authors:  Eray Ozkural <eray@pardus.org.tr>
#           Faik Uygur   <faik@pardus.org.tr>
#
# Extends zipfile module with lzma and bzip2 support

# python standard library modules
import os
import struct
import time
import binascii

from zipfile import *

try:
    import zlib
except ImportError:
    zlib = None

try:
    import bzip2
except ImportError:
    bzip2 = None

try:
    import pylzma
except ImportError:
    pylzma = None

ZIP_BZIP2 = 12
ZIP_LZMA_BOGUS = 255

compression_methods = [ZIP_STORED, ZIP_DEFLATED, ZIP_BZIP2, ZIP_LZMA_BOGUS]

class FileEntry:
    """File-like object used to access entries in a ZipFile"""
    
    def __init__(self, fp, length):
        self.fp = fp
        self.readBytes = 0
        self.returnedBytes = 0
        self.length = length
        self.finished = 0

class LzmaFileEntry(FileEntry):
    """File-like object used to read a LZMA entry in a ZipFile"""

    def __init__(self, fp, length):
        FileEntry.__init__(self, fp, length)
        self.decomp = pylzma.decompressobj()
        self.buffer = ""
        
    def tell(self):
        return self.returnedBytes
    
    def read(self, n=None):
        if self.finished:
            return ""
        if n is None:
            result = [self.buffer,]
            result.append(self.decomp.decompress(self.fp.read(self.length - self.readBytes)))
            result.append(self.decomp.flush())
            self.buffer = ""
            self.finished = 1
            result = "".join(result)
            self.returnedBytes += len(result)
            return result
        else:
            while len(self.buffer) < n:
                data = self.fp.read(min(n, 1024, self.length - self.readBytes))
                self.readBytes += len(data)
                if not data:
                    result = self.buffer + self.decomp.decompress() + self.decomp.flush()
                    self.finished = 1
                    self.buffer = ""
                    self.returnedBytes += len(result)
                    return result
                else:
                    self.buffer += self.decomp.decompress(data)
            result = self.buffer[:n]
            self.buffer = self.buffer[n:]
            self.returnedBytes += len(result)
            return result
    
    def close(self):
        self.finished = 1
        del self.fp

class ZipFileEntry(FileEntry):
    """File-like object used to read an uncompressed entry in a ZipFile"""
    
    def __init__(self, fp, length):
        FileEntry.__init__(self, fp, length)
        
    def tell(self):
        return self.readBytes
    
    def read(self, n=None):
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


class DeflatedZipFileEntry(FileEntry):
    """File-like object used to read a deflated entry in a ZipFile"""
    
    def __init__(self, fp, length):
        FileEntry.__init__(self, fp, length)
        self.decomp = zlib.decompressobj(-15)
        self.buffer = ""
        
    def tell(self):
        return self.returnedBytes
    
    def read(self, n=None):
        if self.finished:
            return ""
        if n is None:
            result = [self.buffer,]
            result.append(self.decomp.decompress(self.fp.read(self.length - self.readBytes)))
            result.append(self.decomp.decompress("Z"))
            result.append(self.decomp.flush())
            self.buffer = ""
            self.finished = 1
            result = "".join(result)
            self.returnedBytes += len(result)
            return result
        else:
            while len(self.buffer) < n:
                data = self.fp.read(min(n, 1024, self.length - self.readBytes))
                self.readBytes += len(data)
                if not data:
                    result = self.buffer + self.decomp.decompress("Z") + self.decomp.flush()
                    self.finished = 1
                    self.buffer = ""
                    self.returnedBytes += len(result)
                    return result
                else:
                    self.buffer += self.decomp.decompress(data)
            result = self.buffer[:n]
            self.buffer = self.buffer[n:]
            self.returnedBytes += len(result)
            return result
    
    def close(self):
        self.finished = 1
        del self.fp

class ZipFileExt(ZipFile):

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
        if zinfo.compress_type not in compression_methods:
            raise RuntimeError, \
                  "Compression method %s is not supported" % zinfo.compress_type
        if zinfo.compress_type == ZIP_DEFLATED and not zlib:
            raise RuntimeError, \
                  "Compression requires the (missing) zlib module"
        if zinfo.compress_type == ZIP_BZIP2 and not bzip2:
            raise RuntimeError, \
                  "Compression requires the (missing) bzip2 module"
        if zinfo.compress_type == ZIP_LZMA_BOGUS and not pylzma:
            raise RuntimeError, \
                  "Compression requires the (missing) pylzma module"

    def write(self, filename, arcname=None, compress_type=None):
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

        # really compress
        if zinfo.compress_type == ZIP_DEFLATED or zinfo.compress_type == ZIP_STORED:  
            if zinfo.compress_type == ZIP_DEFLATED:
                cmpr = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION,
                                        zlib.DEFLATED, -15)            
            else:
                cmpr = None

            while 1:
                buf = fp.read(1024 * 8)
                if not buf:
                    break
                file_size = file_size + len(buf)
                CRC = binascii.crc32(buf, CRC)
                if cmpr:
                    buf = cmpr.compress(buf)
                    compress_size = compress_size + len(buf)
                self.fp.write(buf)
            fp.close()
            if cmpr:
                buf = cmpr.flush()
                compress_size = compress_size + len(buf)
                self.fp.write(buf)
                zinfo.compress_size = compress_size
            else:
                zinfo.compress_size = file_size

        elif zinfo.compress_type == ZIP_LZMA_BOGUS:
            # unfortunately pylzma.compressobj is not implemented yet.
            # So in order to calculate the CRC, we are going to read
            # all the file at once until it is implemented.
            buf = fp.read()
            file_size = len(buf)
            CRC = binascii.crc32(buf, CRC)
            compressed = pylzma.compress(buf, eos=1)
            self.fp.write(compressed)
            zinfo.compress_size = len(compressed)

        zinfo.CRC = CRC
        zinfo.file_size = file_size
        # Seek backwards and write CRC and file sizes
        position = self.fp.tell()       # Preserve current position in file
        self.fp.seek(zinfo.header_offset + 14, 0)
        self.fp.write(struct.pack("<lLL", zinfo.CRC, zinfo.compress_size,
              zinfo.file_size))
        self.fp.seek(position, 0)
        self.filelist.append(zinfo)
        self.NameToInfo[zinfo.filename] = zinfo

    def readfile(self, name):
        """Return file-like object for name."""
        if self.mode not in ("r", "a"):
            raise RuntimeError, 'read() requires mode "r" or "a"'
        if not self.fp:
            raise RuntimeError, \
                  "Attempt to read ZIP archive that was already closed"
        zinfo = self.getinfo(name)
        self.fp.seek(zinfo.file_offset, 0)
        if zinfo.compress_type == ZIP_STORED:
            return ZipFileEntry(self.fp, zinfo.compress_size)
        elif zinfo.compress_type == ZIP_DEFLATED:
            if not zlib:
                raise RuntimeError, \
                      "De-compression requires the (missing) zlib module"
            return DeflatedZipFileEntry(self.fp, zinfo.compress_size)
##        elif zinfo.compress_type == ZIP_BZIP2:
##            if not bzip2:
##                raise RuntimeError, \
##                      "De-compression requires the (missing) bzip2 module"
##          return LZMAFileEntry(self.fp, zinfo.compress_size)
        elif zinfo.compress_type == ZIP_LZMA_BOGUS:
            if not pylzma:
                raise RuntimeError, \
                      "De-compression requires the (missing) pylzma module"
            return LzmaFileEntry(self.fp, zinfo.compress_size)
        else:
            raise BadZipfile, \
                  "Unsupported compression method %d for file %s" % \
            (zinfo.compress_type, name)

    def read(self, name):
        """Return file bytes (as a string) for name."""
        f = self.readfile(name)
        zinfo = self.getinfo(name)
        bytes = f.read()
        crc = binascii.crc32(bytes)
        if crc != zinfo.CRC:
            raise BadZipfile, "Bad CRC-32 for file %s" % name
        return bytes
