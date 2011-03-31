# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2011, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

"""Archive module provides access to regular archive file types."""

# standard library modules
import os
import stat
import shutil
import tarfile
import zipfile

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

# PiSi modules
import pisi
import pisi.util as util
import pisi.context as ctx


class UnknownArchiveType(Exception):
    pass


# Proxy class inspired from tarfile._BZ2Proxy
class _LZMAProxy(object):

    blocksize = 16 * 1024

    def __init__(self, fileobj, mode):
        self.fileobj = fileobj
        self.mode = mode
        self.name = getattr(self.fileobj, "name", None)
        self.init()

    def init(self):
        import lzma
        self.pos = 0
        if self.mode == "r":
            self.lzmaobj = lzma.LZMADecompressor()
            # Seeking here can cause problems with Python 2.7
            # if hasattr(self.fileobj, "seek"):
            #     self.fileobj.seek(0)
            self.buf = ""
        else:
            self.lzmaobj = lzma.LZMACompressor()

    def read(self, size):
        b = [self.buf]
        x = len(self.buf)
        while x < size:
            raw = self.fileobj.read(self.blocksize)
            if not raw:
                break
            try:
                data = self.lzmaobj.decompress(raw)
            except EOFError:
                break
            b.append(data)
            x += len(data)
        self.buf = "".join(b)

        buf = self.buf[:size]
        self.buf = self.buf[size:]
        self.pos += len(buf)
        return buf

    def seek(self, pos):
        if pos < self.pos:
            self.init()
        self.read(pos - self.pos)

    def tell(self):
        return self.pos

    def write(self, data):
        self.pos += len(data)
        raw = self.lzmaobj.compress(data)
        self.fileobj.write(raw)

    def close(self):
        if self.mode == "w":
            raw = self.lzmaobj.flush()
            self.fileobj.write(raw)


class TarFile(tarfile.TarFile):

    @classmethod
    def lzmaopen(cls,
                 name=None,
                 mode="r",
                 fileobj=None,
                 compressformat="xz",
                 compresslevel=9,
                 **kwargs):
        """Open lzma/xz compressed tar archive name for reading or writing.
           Appending is not allowed.
        """

        if len(mode) > 1 or mode not in "rw":
            raise ValueError("mode must be 'r' or 'w'.")

        try:
            import lzma
        except ImportError:
            raise tarfile.CompressionError("lzma module is not available")

        if fileobj is not None:
            fileobj = _LZMAProxy(fileobj, mode)
        else:
            options = {"format":    compressformat,
                       "level":     compresslevel}
            fileobj = lzma.LZMAFile(name, mode, options=options)

        try:
            t = cls.taropen(name, mode, fileobj, **kwargs)
        except IOError:
            raise ReadError("not a lzma file")
        t._extfileobj = False
        return t


class ArchiveBase(object):
    """Base class for Archive classes."""
    def __init__(self, file_path, atype):
        self.file_path = file_path
        self.type = atype

    def unpack(self, target_dir, clean_dir=False):
        self.target_dir = target_dir
        # first we check if we need to clean-up our working env.
        if os.path.exists(self.target_dir):
            if clean_dir:
                util.clean_dir(self.target_dir)

        if not os.path.exists(self.target_dir):
            os.makedirs(self.target_dir)


class ArchiveBinary(ArchiveBase):
    """ArchiveBinary handles binary archive files (usually distributed as
    .bin files)"""
    def __init__(self, file_path, arch_type="binary"):
        super(ArchiveBinary, self).__init__(file_path, arch_type)

    def unpack(self, target_dir, clean_dir=False):
        super(ArchiveBinary, self).unpack(target_dir, clean_dir)

        # we can't unpack .bin files. we'll just move them to target
        # directory and leave the dirty job to actions.py ;)
        target_file = os.path.join(target_dir,
                                   os.path.basename(self.file_path))
        shutil.copyfile(self.file_path, target_file)


class ArchiveBzip2(ArchiveBase):
    """ArchiveBzip2 handles Bzip2 archive files"""

    def __init__(self, file_path, arch_type="bz2"):
        super(ArchiveBzip2, self).__init__(file_path, arch_type)

    def unpack(self, target_dir, clean_dir=False):
        super(ArchiveBzip2, self).unpack(target_dir, clean_dir)
        self.unpack_dir(target_dir)

    def unpack_dir(self, target_dir):
        """Unpack Bzip2 archive to a given target directory(target_dir)."""

        output_path = util.join_path(target_dir,
                                     os.path.basename(self.file_path))
        if output_path.endswith(".bz2"):
            output_path = output_path[:-4]

        import bz2
        bz2_file = bz2.BZ2File(self.file_path, "r")
        output = open(output_path, "w")
        output.write(bz2_file.read())
        output.close()
        bz2_file.close()


class ArchiveGzip(ArchiveBase):
    """ArchiveGzip handles Gzip archive files"""

    def __init__(self, file_path, arch_type="gz"):
        super(ArchiveGzip, self).__init__(file_path, arch_type)

    def unpack(self, target_dir, clean_dir=False):
        super(ArchiveGzip, self).unpack(target_dir, clean_dir)
        self.unpack_dir(target_dir)

    def unpack_dir(self, target_dir):
        """Unpack Gzip archive to a given target directory(target_dir)."""

        output_path = util.join_path(target_dir,
                                     os.path.basename(self.file_path))
        if output_path.endswith(".gz"):
            output_path = output_path[:-3]

        import gzip
        gzip_file = gzip.GzipFile(self.file_path, "r")
        output = open(output_path, "w")
        output.write(gzip_file.read())
        output.close()
        gzip_file.close()


class ArchiveLzma(ArchiveBase):
    """ArchiveLzma handles LZMA archive files"""

    def __init__(self, file_path, arch_type="lzma"):
        super(ArchiveLzma, self).__init__(file_path, arch_type)

    def unpack(self, target_dir, clean_dir=False):
        super(ArchiveLzma, self).unpack(target_dir, clean_dir)
        self.unpack_dir(target_dir)

    def unpack_dir(self, target_dir):
        """Unpack LZMA archive to a given target directory(target_dir)."""

        output_path = util.join_path(target_dir,
                                     os.path.basename(self.file_path))
        ext = ".lzma" if self.type == "lzma" else ".xz"
        if output_path.endswith(ext):
            output_path = output_path[:-len(ext)]

        import lzma
        lzma_file = lzma.LZMAFile(self.file_path, "r")
        output = open(output_path, "w")
        output.write(lzma_file.read())
        output.close()
        lzma_file.close()


class ArchiveTar(ArchiveBase):
    """ArchiveTar handles tar archives depending on the compression
    type. Provides access to tar, tar.gz and tar.bz2 files.

    This class provides the unpack magic for tar archives."""
    def __init__(self, file_path=None, arch_type="tar",
                        no_same_permissions=True,
                        no_same_owner=True,
                        fileobj=None):
        super(ArchiveTar, self).__init__(file_path, arch_type)
        self.tar = None
        self.no_same_permissions = no_same_permissions
        self.no_same_owner = no_same_owner
        self.fileobj = fileobj

    def unpack(self, target_dir, clean_dir=False):
        """Unpack tar archive to a given target directory(target_dir)."""
        super(ArchiveTar, self).unpack(target_dir, clean_dir)
        self.unpack_dir(target_dir)

    def unpack_dir(self, target_dir, callback=None):
        rmode = ""
        self.tar = None
        if self.type == 'tar':
            rmode = 'r:'
        elif self.type == 'targz':
            rmode = 'r:gz'
        elif self.type == 'tarbz2':
            rmode = 'r:bz2'
        elif self.type in ('tarlzma', 'tarxz'):
            self.tar = TarFile.lzmaopen(self.file_path, fileobj=self.fileobj)
        else:
            raise UnknownArchiveType

        if self.tar is None:
            self.tar = tarfile.open(self.file_path, rmode,
                                    fileobj=self.fileobj)

        oldwd = None
        try:
            # Don't fail if CWD doesn't exist (#6748)
            oldwd = os.getcwd()
        except OSError:
            pass
        os.chdir(target_dir)

        uid = os.getuid()
        gid = os.getgid()

        for tarinfo in self.tar:
            if callback:
                callback(tarinfo, extracted=False)

            if tarinfo.issym() and \
                    os.path.isdir(tarinfo.name) and \
                    not os.path.islink(tarinfo.name):
                # Changing a directory with a symlink. tarfile module
                # cannot handle this case.

                if os.path.isdir(tarinfo.linkname):
                    # Symlink target is a directory. Move old directory's
                    # content to this directory.
                    for filename in os.listdir(tarinfo.name):
                        old_path = util.join_path(tarinfo.name, filename)
                        new_path = util.join_path(tarinfo.linkname, filename)

                        if os.path.lexists(new_path):
                            if not os.path.isdir(new_path):
                                # A file with the same name exists in the
                                # target. Remove the one in the old directory.
                                os.remove(old_path)
                            continue

                        os.renames(old_path, new_path)

                    os.rmdir(tarinfo.name)

                elif not os.path.lexists(tarinfo.linkname):
                    # Symlink target does not exist. Assume the old
                    # directory is moved to another place in package.
                    os.renames(tarinfo.name, tarinfo.linkname)

                else:
                    # This should not happen. Probably a packaging error.
                    # Try to rename directory
                    try:
                        os.rename(tarinfo.name,
                                  "%s.renamed-by-pisi" % tarinfo.name)
                    except:
                        # If fails, try to remove it
                        shutil.rmtree(tarinfo.name)

            self.tar.extract(tarinfo)

            # tarfile.extract does not honor umask. It must be honored
            # explicitly. See --no-same-permissions option of tar(1),
            # which is the deafult behaviour.
            #
            # Note: This is no good while installing a pisi package.
            # Thats why this is optional.
            if self.no_same_permissions and not os.path.islink(tarinfo.name):
                os.chmod(tarinfo.name, tarinfo.mode & ~ctx.const.umask)

            if self.no_same_owner:
                if not os.path.islink(tarinfo.name):
                    os.chown(tarinfo.name, uid, gid)
                else:
                    os.lchown(tarinfo.name, uid, gid)

            if callback:
                callback(tarinfo, extracted=True)

        try:
            if oldwd:
                os.chdir(oldwd)
        # Bug #6748
        except OSError:
            pass
        self.close()

    def add_to_archive(self, file_name, arc_name=None):
        """Add file or directory path to the tar archive"""
        if not self.tar:
            if self.type == 'tar':
                wmode = 'w:'
            elif self.type == 'targz':
                wmode = 'w:gz'
            elif self.type == 'tarbz2':
                wmode = 'w:bz2'
            elif self.type in ('tarlzma', 'tarxz'):
                format = "xz" if self.type == "tarxz" else "alone"
                level = int(ctx.config.values.build.compressionlevel)
                self.tar = TarFile.lzmaopen(self.file_path, "w",
                                            fileobj=self.fileobj,
                                            compressformat=format,
                                            compresslevel=level)
            else:
                raise UnknownArchiveType

            if self.tar is None:
                self.tar = tarfile.open(self.file_path, wmode,
                                        fileobj=self.fileobj)

        self.tar.add(file_name, arc_name)

    def close(self):
        self.tar.close()


class ArchiveTarZ(ArchiveBase):
    """ArchiveTar handles tar.Z archives.

    This class provides the unpack magic for tar.Z archives."""
    def __init__(self, file_path, arch_type="tarZ",
                        no_same_permissions=True, no_same_owner=True):
        super(ArchiveTarZ, self).__init__(file_path, arch_type)
        self.tar = None
        self.no_same_permissions = no_same_permissions
        self.no_same_owner = no_same_owner

    def unpack(self, target_dir, clean_dir=False):
        """Unpack tar archive to a given target directory(target_dir)."""
        super(ArchiveTarZ, self).unpack(target_dir, clean_dir)
        self.unpack_dir(target_dir)

    def unpack_dir(self, target_dir):
        self.file_path = util.remove_suffix(".Z", self.file_path)

        ret, out, err = util.run_batch(
                "uncompress -cf %s.Z > %s" % (self.file_path, self.file_path))
        if ret != 0:
            raise RuntimeError(
                        _("Problem occured while uncompressing %s.Z file")
                        % self.file_path)

        self.tar = tarfile.open(self.file_path)

        oldwd = None
        try:
            # Don't fail if CWD doesn't exist (#6748)
            oldwd = os.getcwd()
        except OSError:
            pass
        os.chdir(target_dir)

        uid = os.getuid()
        gid = os.getgid()

        for tarinfo in self.tar:
            self.tar.extract(tarinfo)

            # tarfile.extract does not honor umask. It must be honored
            # explicitly. See --no-same-permissions option of tar(1),
            # which is the deafult behaviour.
            #
            # Note: This is no good while installing a pisi package.
            # Thats why this is optional.
            if self.no_same_permissions and not os.path.islink(tarinfo.name):
                os.chmod(tarinfo.name, tarinfo.mode & ~ctx.const.umask)

            if self.no_same_owner:
                if not os.path.islink(tarinfo.name):
                    os.chown(tarinfo.name, uid, gid)
                else:
                    os.lchown(tarinfo.name, uid, gid)

        # Bug #10680 and addition for tarZ files
        os.unlink(self.file_path)

        try:
            if oldwd:
                os.chdir(oldwd)
        # Bug #6748
        except OSError:
            pass
        self.tar.close()


class ArchiveZip(ArchiveBase):
    """ArchiveZip handles zip archives.

    Being a zip archive PiSi packages also use this class
    extensively. This class provides unpacking and packing magic for
    zip archives."""

    symmagic = 2716663808  # long of hex val '0xA1ED0000L'

    def __init__(self, file_path, arch_type="zip", mode='r'):
        super(ArchiveZip, self).__init__(file_path, arch_type)

        self.zip_obj = zipfile.ZipFile(self.file_path, mode)

    def open(self, file_path, mode="r"):
        return self.zip_obj.open(file_path, mode)

    def close(self):
        """Close the zip archive."""
        self.zip_obj.close()

    def add_to_archive(self, file_name, arc_name=None):
        """Add file or directory path to the zip file"""
        # It's a pity that zipfile can't handle unicode strings. Grrr!
        file_name = str(file_name)
        if os.path.isdir(file_name) and not os.path.islink(file_name):
            arc_name = arc_name or ""
            self.zip_obj.writestr(arc_name + '/', '')
            attr_obj = self.zip_obj.getinfo(arc_name + '/')
            attr_obj.external_attr = stat.S_IMODE(os.stat(file_name)[0]) << 16L
            for f in os.listdir(file_name):
                self.add_to_archive(os.path.join(file_name, f),
                                    os.path.join(arc_name, f))
        else:
            if os.path.islink(file_name):
                dest = os.readlink(file_name)
                attr = zipfile.ZipInfo()
                attr.filename = file_name
                attr.create_system = 3
                attr.external_attr = self.symmagic
                self.zip_obj.writestr(attr, dest)
            else:
                comp_type = zipfile.ZIP_DEFLATED
                if file_name.endswith((ctx.const.lzma_suffix,
                                       ctx.const.xz_suffix)):
                    comp_type = zipfile.ZIP_STORED
                self.zip_obj.write(file_name, arc_name, comp_type)

                if not arc_name:
                    zinfo = self.zip_obj.getinfo(file_name)
                else:
                    zinfo = self.zip_obj.getinfo(arc_name)
                zinfo.create_system = 3

    def add_basename_to_archive(self, file_name):
        """Add only the basepath to the zip file. For example; if the given
        file_name parameter is /usr/local/bin/somedir, this function
        will create only the base directory/file somedir in the
        archive."""
        cwd = os.getcwd()
        path_name = os.path.dirname(file_name)
        file_name = os.path.basename(file_name)
        if path_name:
            os.chdir(path_name)
        self.add_to_archive(file_name)
        os.chdir(cwd)

    def has_file(self, file_path):
        """ Returns true if file_path is member of the zip archive"""
        return file_path in self.zip_obj.namelist()

    def read_file(self, file_path):
        return self.zip_obj.read(file_path)

    def unpack_file_cond(self, pred, target_dir, archive_root=''):
        """Unpack/Extract files according to predicate function
        pred: filename -> bool
        unpacks stuff into target_dir and only extracts files
        from archive_root, treating it as the archive root"""
        zip_obj = self.zip_obj
        for info in zip_obj.infolist():
            if pred(info.filename):   # check if condition holds

                # below code removes that, so we find it here
                is_dir = info.filename.endswith('/')

                # calculate output file name
                if archive_root == '':
                    outpath = info.filename
                else:
                    # change archive_root
                    if util.subpath(archive_root, info.filename):
                        outpath = util.removepathprefix(archive_root,
                                                        info.filename)
                    else:
                        continue        # don't extract if not under

                ofile = os.path.join(target_dir, outpath)

                if is_dir:               # this is a directory
                    if not os.path.isdir(ofile):
                        os.makedirs(ofile)
                        perm = info.external_attr
                        perm &= 0xFFFF0000
                        perm >>= 16
                        perm |= 0x00000100
                        os.chmod(ofile, perm)
                    continue

                # check that output dir is present
                util.ensure_dirs(os.path.dirname(ofile))

                # remove output file we might be overwriting.
                # (also check for islink? for broken symlinks...)
                if os.path.isfile(ofile) or os.path.islink(ofile):
                    os.remove(ofile)

                if info.external_attr == self.symmagic:
                    if os.path.isdir(ofile):
                        # A rare case, the file used to be a dir,
                        # now it is a symlink!
                        shutil.rmtree(ofile)
                    target = zip_obj.read(info.filename)
                    os.symlink(target, ofile)
                else:
                    perm = info.external_attr
                    perm &= 0x08FF0000
                    perm >>= 16
                    perm |= 0x00000100

                    info.filename = outpath
                    zip_obj.extract(info, target_dir)
                    os.chmod(ofile, perm)

    def unpack_files(self, paths, target_dir):
        self.unpack_file_cond(lambda f: f in paths, target_dir)

    def unpack_dir(self, path, target_dir):
        self.unpack_file_cond(lambda f: util.subpath(path, f), target_dir)

    def unpack_dir_flat(self, path, target_dir):
        self.unpack_file_cond(lambda f: util.subpath(path, f),
                              target_dir, path)

    def unpack(self, target_dir, clean_dir=False):
        super(ArchiveZip, self).unpack(target_dir, clean_dir)

        self.unpack_file_cond(lambda f: True, target_dir)
        self.close()
        return


class Archive:
    """Archive is the main factory for ArchiveClasses, regarding the
    Abstract Factory Pattern :)."""

    def __init__(self, file_path, arch_type):
        """Accepted archive types:
        targz, tarbz2, tarlzma, tarxz, tarZ, tar, zip, gzip, bzip2,
        lzma, xz, binary"""

        if not arch_type:
            arch_type = self._guess_archive_type(file_path)

        handlers = {'targz':    ArchiveTar,
                    'tarbz2':   ArchiveTar,
                    'tarlzma':  ArchiveTar,
                    'tarxz':    ArchiveTar,
                    'tarZ':     ArchiveTarZ,
                    'tar':      ArchiveTar,
                    'zip':      ArchiveZip,
                    'gz':       ArchiveGzip,
                    'gzip':     ArchiveGzip,
                    'bz2':      ArchiveBzip2,
                    'bzip2':    ArchiveBzip2,
                    'lzma':     ArchiveLzma,
                    'xz':       ArchiveLzma,
                    'binary':   ArchiveBinary}

        handler = handlers.get(arch_type)
        if handler is None:
            raise UnknownArchiveType

        self.archive = handler(file_path, arch_type)

    def _guess_archive_type(self, file_path):
        types = (("targz",      (".tar.gz", ".tgz")),
                 ("tarbz2",     (".tar.bz2", ".tar.bz", ".tbz2", ".tbz")),
                 ("tarlzma",    (".tar.lzma", ".tlz")),
                 ("tarxz",      (".tar.xz", ".txz")),
                 ("tarZ",       (".tar.Z",)),
                 ("tar",        (".tar",)),
                 ("zip",        (".zip", ".ZIP")),
                 ("gz",         (".gz",)),
                 ("bz2",        (".bz2", ".bz")),
                 ("lzma",       (".lzma",)),
                 ("xz",         (".xz",)),
                 ("binary",     (".bin", ".run", ".sh")))

        for _type, extensions in types:
            if file_path.endswith(extensions):
                return _type

        return "binary"

    def unpack(self, target_dir, clean_dir=False):
        self.archive.unpack(target_dir, clean_dir)

    def unpack_files(self, files, target_dir):
        self.archive.unpack_files(files, target_dir)
