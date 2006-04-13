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
# Extends zipfile module with 7zip and bzip2 support

# python standard library modules
import os
import struct
import time

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
ZIP_7ZIP = 255

compression_methods = [ZIP_STORED, ZIP_DEFLATED, ZIP_BZIP2, ZIP_7ZIP]

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
        if zinfo.compress_type == ZIP_7ZIP and not pylzma:
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
        elif zinfo.compress_type == ZIP_7ZIP:
            cmp_fp = pylzma.compressfile(fp, eos=1)
            compressed = ''
            while True:
                tmp = cmp_fp.read(1)
                if not tmp: 
                    break
                compressed += tmp
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
