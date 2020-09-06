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

"""Archive module provides access to regular archive file types."""

# INARY modules
import inary.uri
import inary.errors
import inary.fetcher
import inary.util as util
import inary.context as ctx

# Standard Python Modules
import os
import lzma
import stat
import errno
import shutil
import tarfile
import zipfile

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class SourceArchiveError(inary.errors.Error):
    pass


class UnknownArchiveType(Exception):
    pass


class ArchiveHandlerNotInstalled(Exception):
    pass


# Proxy class inspired from tarfile._BZ2Proxy

class _LZMAProxy(object):
    """Small proxy class that enables external file object
       support for "r:bz2" and "w:bz2" modes. This is actually
       a workaround for a limitation in bz2 module's BZ2File
       class which (unlike gzip.GzipFile) has no support for
       a file object argument.
    """

    blocksize = 16 * 1024

    def __init__(self, fileobj, mode):
        self.fileobj = fileobj
        self.mode = mode
        self.name = getattr(self.fileobj, "name", None)
        self.init()

    def init(self):
        self.pos = 0
        if self.mode == "r":
            self.lzmaobj = lzma.LZMADecompressor()
            # self.fileobj.seek(0)
            self.buf = b""
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
                if self.lzmaobj.__class__ == lzma.LZMADecompressor:
                    data = self.lzmaobj.decompress(raw)
            except EOFError:
                break
            b.append(data)
            x += len(data)
        self.buf = b"".join(b)

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
                 compresslevel=None,
                 **kwargs):
        """Open lzma/xz compressed tar archive name for reading or writing.
           Appending is not allowed.
        """

        try:
            import lzma
        except ImportError:
            try:
                from backports import lzma
            except ImportError:
                raise tarfile.CompressionError("Lzma module is not available")

        if not compresslevel:
            compresslevel = ctx.config.values.build.compressionlevel

        if len(mode) > 1 or mode not in "rw":
            raise ValueError("mode must be 'r' or 'w'.")

        if 'w' in mode:
            if fileobj is not None:
                fileobj = _LZMAProxy(fileobj, mode)
            else:
                fileobj = lzma.LZMAFile(name, mode, preset=compresslevel)

        else:
            if fileobj is not None:
                fileobj = _LZMAProxy(fileobj, mode)
            else:
                fileobj = lzma.LZMAFile(name, mode)

        try:
            t = cls.taropen(name, mode, fileobj, **kwargs)
        except IOError:
            raise tarfile.ReadError(
                _(" \"{}\" is not a lzma file.").format(name))
        t._extfileobj = False
        return t


class ArchiveBase(object):
    """Base class for Archive classes."""

    def __init__(self, file_path, atype):
        self.file_path = file_path
        self.type = atype

    def unpack(self, target_dir, clean_dir=False):
        # first we check if we need to clean-up our working env.
        if os.path.exists(target_dir):
            if clean_dir:
                util.clean_dir(target_dir)

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)


class ArchiveBinary(ArchiveBase):
    """ArchiveBinary handles binary archive files (usually distributed as
    .bin files)"""

    def __init__(self, file_path, arch_type="binary"):
        super(ArchiveBinary, self).__init__(file_path, arch_type)

    def unpack(self, target_dir, clean_dir=False):
        super(ArchiveBinary, self).unpack(target_dir, clean_dir)

        # we can't unpack .bin files. we'll just move them to target
        # directory and leave the dirty job to actions.py ;)
        print(target_dir)
        target_file = os.path.join(target_dir,
                                   os.path.basename(self.file_path))
        if os.path.isfile(self.file_path):
            shutil.copyfile(self.file_path, target_file)
        elif os.path.isdir(self.file_path):
            shutil.copytree(self.file_path, target_file)


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
        bz2_file = bz2.BZ2File(self.file_path)
        output = open(output_path, "w")
        output.write(bz2_file.read().decode("utf-8"))
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
        output.write(gzip_file.read().decode("utf-8"))
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

        lzma_file = lzma.LZMAFile(self.file_path)
        output = open(output_path, "w")
        output.write(lzma_file.read().decode("utf-8"))
        output.close()
        lzma_file.close()


def __chown(name, uid, gid):
    if not os.path.islink(name):
        ctx.ui.info(
            _("Chowning {0} ({1}:{2})").format(
                name, uid, gid), verbose=True)
        os.chown(name, uid, gid)
    else:
        ctx.ui.info(
            _("LChowning {0} ({1}:{2})").format(
                name, uid, gid), verbose=True)
        os.lchown(name, uid, gid)


class ArchiveTar(ArchiveBase):
    """ArchiveTar handles tar archives depending on the compression
    type. Provides access to tar, tar.gz and tar.bz2 files.

    This class provides the unpack magic for tar archives."""

    def __init__(self, file_path=None, arch_type="tar",
                 no_same_permissions=True,
                 no_same_owner=False,
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

    def maybe_nuke_pip(self, info):
        if not info.name.endswith(".egg-info"):
            return
        if "site-packages" not in info.name:
            return
        if "/python" not in info.name:
            return
        if not info.isreg():
            return
        if not os.path.isdir(info.name):
            return
        print("Overwriting stale pip install: /{}".format(info.name))
        shutil.rmtree(info.name)

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
                                    fileobj=self.fileobj, errorlevel=1)

        oldwd = None
        try:
            # Don't fail if CWD doesn't exist (#6748)
            oldwd = os.getcwd()
        except OSError:
            pass

        ctx.ui.info(_("Target DIR: \"{}\"").format(target_dir), verbose=True)
        os.chdir(target_dir)

        for tarinfo in self.tar:
            if callback:
                callback(tarinfo, extracted=False)

            startservices = []
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

                        # try as up to this time
                        try:
                            os.renames(old_path, new_path)
                        except OSError as e:
                            # something gone wrong? [Errno 18] Invalid cross-device link?
                            # try in other way
                            if e.errno == errno.EXDEV:
                                if tarinfo.linkname.startswith(".."):
                                    new_path = util.join_path(
                                        os.path.normpath(
                                            os.path.join(
                                                os.path.dirname(
                                                    tarinfo.name),
                                                tarinfo.linkname)),
                                        filename)
                                if not old_path.startswith("/"):
                                    old_path = "/" + old_path
                                if not new_path.startswith("/"):
                                    new_path = "/" + new_path
                                print("Moving:", old_path, " -> ", new_path)
                                os.system(
                                    "mv -f {0} {1}".format(old_path, new_path))
                            else:
                                raise
                    try:
                        os.rmdir(tarinfo.name)
                    except OSError as e:
                        # hmmm, not empty dir? try rename it adding .old
                        # extension.
                        if e.errno == errno.ENOTEMPTY:
                            # if directory with dbus/pid file was moved we have
                            # to restart dbus
                            for (path, dirs, files) in os.walk(tarinfo.name):
                                if path.endswith("dbus") and "pid" in files:
                                    startservices.append("dbus")
                                    for service in (
                                            "NetworkManager", "connman", "wicd"):
                                        # FIXME: It needs a quick fix for
                                        # openrc
                                        if os.path.isfile(
                                                "/etc/scom/services/enabled/{}".format(service)):
                                            startservices.append(service)
                                            os.system(
                                                "service {} stop".format(service))
                                    os.system("service dbus stop")
                                    break
                            os.system("mv -f {0} {0}.old".format(tarinfo.name))
                        else:
                            raise

                elif not os.path.lexists(tarinfo.linkname):
                    # Symlink target does not exist. Assume the old
                    # directory is moved to another place in package.
                    os.renames(tarinfo.name, tarinfo.linkname)

                else:
                    # This should not happen. Probably a packaging error.
                    # Try to rename directory
                    try:
                        os.rename(tarinfo.name,
                                  "{}.renamed-by-inary".format(tarinfo.name))
                    except BaseException:
                        # If fails, try to remove it
                        shutil.rmtree(tarinfo.name)

            try:
                if not os.path.isdir(tarinfo.name) and not os.path.islink(tarinfo.name):
                    try:
                        os.unlink(tarinfo.name)
                    except:
                        # TODO: review this block
                        pass
                    self.tar.extract(tarinfo)
            except IOError as e:
                os.remove(tarinfo.name)
                self.tar.extract(tarinfo)
            except OSError as e:
                # Handle the case where an upper directory cannot
                # be created because of a conflict with an existing
                # regular file or symlink. In this case, remove
                # the old file and retry extracting.

                if e.errno != errno.EEXIST:
                    raise

                # For the path "a/b/c", upper_dirs will be ["a", "a/b"].
                upper_dirs = []
                head, tail = os.path.split(tarinfo.name)

                while head and tail:
                    upper_dirs.insert(0, head)
                    head, tail = os.path.split(head)

                for path in upper_dirs:
                    if not os.path.lexists(path):
                        break

                    if not os.path.isdir(path):
                        # A file with the same name exists.
                        # Remove the existing file.
                        os.remove(path)
                        break
                else:
                    # No conflicts detected! This is probably not the case
                    # mentioned here. Raise the same exception.
                    raise

                # Try to extract again.
                self.tar.extract(tarinfo)

                # Handle the case where new path is file, but old path is directory
                # due to not possible touch file c in /a/b if directory /a/b/c
                # exists.
                if not e.errno == errno.EISDIR:
                    path = tarinfo.name
                    found = False
                    while path:
                        if os.path.isfile(path):
                            os.unlink(path)
                            found = True
                            break
                        else:
                            path = "/".join(path.split("/")[:-1])
                    if not found:
                        raise
                    # Try to extract again.
                    self.tar.extract(tarinfo)
                else:
                    shutil.rmtree(tarinfo.name)
                    # Try to extract again.
                    self.tar.extract(tarinfo)

            # tarfile.extract does not honor umask. It must be honored
            # explicitly. See --no-same-permissions option of tar(1),
            # which is the deafult behaviour.
            #
            # Note: This is no good while installing a inary package.
            # Thats why this is optional.
            if self.no_same_permissions and not os.path.islink(tarinfo.name):
                os.chmod(tarinfo.name, tarinfo.mode & ~ctx.const.umask)

            if self.no_same_owner:
                uid = os.getuid()
                gid = os.getgid()
                __chown(tarinfo.name, uid, gid)

                if not os.path.islink(tarinfo.name):
                    ctx.ui.info(
                        _("Chowning {0} ({1}:{2})").format(
                            tarinfo.name, uid, gid), verbose=True)
                    os.chown(tarinfo.name, uid, gid)
                else:
                    ctx.ui.info(
                        _("LChowning {0} ({1}:{2})").format(
                            tarinfo.name, uid, gid), verbose=True)
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
                compresslevel = int(ctx.config.values.build.compressionlevel)
                self.tar = TarFile.lzmaopen(self.file_path, "w",
                                            fileobj=self.fileobj,
                                            compresslevel=compresslevel
                                            )
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

        result = util.run_batch(
            "uncompress -cf {0}.Z > {0}".format(self.file_path))
        if result[0] != 0:
            raise RuntimeError(
                _("Problem occured while uncompressing \"{}.Z\" file.\nError:{}").format(
                    self.file_path, result[2]))

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
            # Note: This is no good while installing a inary package.
            # Thats why this is optional.
            if self.no_same_permissions and not os.path.islink(tarinfo.name):
                os.chmod(tarinfo.name, tarinfo.mode & ~ctx.const.umask)

            if self.no_same_owner:
                __chown(tarinfo.name, uid, gid)

        # Bug #10680 and addition for tarZ files
        os.unlink(self.file_path)

        try:
            if oldwd:
                os.chdir(oldwd)
        # Bug #6748
        except OSError:
            pass
        self.tar.close()


class Archive7Zip(ArchiveBase):
    """Archive7Zip handles 7-Zip archives."""

    def __init__(self, file_path, arch_type="7z"):
        super(Archive7Zip, self).__init__(file_path, arch_type)
        self.cmd = util.search_executable(arch_type)
        if not self.cmd:
            raise ArchiveHandlerNotInstalled

    def unpack(self, target_dir, clean_dir=False):
        super(Archive7Zip, self).unpack(target_dir, clean_dir)
        self.unpack_dir(target_dir)

    def unpack_dir(self, target_dir):
        """Unpack 7z archive to a given target directory(target_dir)."""

        # e.g. 7z x -bd -o<target_directory> <archive.7z>
        util.run_batch("{0} x -bd -o{1} {2}".format(self.cmd,
                                                    target_dir, self.file_path))


class ArchiveZip(ArchiveBase):
    """ArchiveZip handles zip archives.

    Being a zip archive INARY packages also use this class
    extensively. This class provides unpacking and packing magic for
    zip archives."""

    symmagic = 2716663808  # long of hex val '0xA1ED0000L'

    def __init__(self, file_path, arch_type="zip", mode='r'):
        super(ArchiveZip, self).__init__(file_path, arch_type)
        try:
            self.zip_obj = zipfile.ZipFile(self.file_path, mode)
        except zipfile.BadZipFile:
            raise UnknownArchiveType(
                _("File \"{}\" is not a zip file.").format(
                    self.file_path))

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
            attr_obj.external_attr = stat.S_IMODE(os.stat(file_name)[0]) << 16
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
        return self.zip_obj.read(file_path).decode('utf-8')

    def unpack_file_cond(self, pred, target_dir, archive_root=''):
        """Unpack/Extract files according to predicate function
        pred: filename -> bool
        unpacks stuff into target_dir and only extracts files
        from archive_root, treating it as the archive root"""
        for info in self.zip_obj.infolist():
            if pred(info.filename):  # check if condition holds

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
                        continue  # don't extract if not under

                ofile = os.path.join(target_dir, outpath)

                if is_dir:  # this is a directory
                    if not os.path.isdir(ofile):
                        os.makedirs(ofile)
                        perm = info.external_attr >> 16
                        if perm == 0:
                            perm = 33261  # octets of -rwxr-xr-x
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
                    target = self.zip_obj.read(info.filename)
                    os.symlink(target, ofile)
                else:
                    perm = info.external_attr >> 16
                    if perm == 0:
                        perm = 33261  # -rwxr-xr-x
                    info.filename = outpath
                    self.zip_obj.extract(info, target_dir)
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

        handlers = {'targz': ArchiveTar,
                    'tarbz2': ArchiveTar,
                    'tarlzma': ArchiveTar,
                    'tarxz': ArchiveTar,
                    'tarZ': ArchiveTarZ,
                    'tar': ArchiveTar,
                    'zip': ArchiveZip,
                    'gz': ArchiveGzip,
                    'gzip': ArchiveGzip,
                    'bz2': ArchiveBzip2,
                    'bzip2': ArchiveBzip2,
                    'lzma': ArchiveLzma,
                    'xz': ArchiveLzma,
                    '7z': Archive7Zip,
                    'binary': ArchiveBinary}

        handler = handlers.get(arch_type)
        if handler is None:
            raise UnknownArchiveType

        self.archive = handler(file_path, arch_type)

    @staticmethod
    def _guess_archive_type(file_path):
        types = (("targz", (".tar.gz", ".tgz")),
                 ("tarbz2", (".tar.bz2", ".tar.bz", ".tbz2", ".tbz")),
                 ("tarlzma", (".tar.lzma", ".tlz")),
                 ("tarxz", (".tar.xz", ".txz")),
                 ("tarZ", (".tar.Z",)),
                 ("tar", (".tar",)),
                 ("zip", (".zip", ".ZIP")),
                 ("gz", (".gz",)),
                 ("bz2", (".bz2", ".bz")),
                 ("lzma", (".lzma",)),
                 ("xz", (".xz",)),
                 ("7z", (".7z",)),
                 ("binary", (".bin", ".run", ".sh")))

        for _type, extensions in types:
            if file_path.endswith(extensions):
                return _type

        return "binary"

    def unpack(self, target_dir, clean_dir=False):
        self.archive.unpack(target_dir, clean_dir)

    def unpack_files(self, files, target_dir):
        self.archive.unpack_files(files, target_dir)


class SourceArchives:
    """This is a wrapper for supporting multiple SourceArchive objects."""

    def __init__(self, spec):
        self.sourceArchives = [SourceArchive(a) for a in spec.source.archive]

    def fetch(self, interactive=True):
        for archive in self.sourceArchives:
            archive.fetch(interactive)

    def unpack(self, target_dir, clean_dir=True):
        self.sourceArchives[0].unpack(target_dir, clean_dir)
        for archive in self.sourceArchives[1:]:
            archive.unpack(target_dir, clean_dir=False)


class SourceArchive:
    """source archive. this is a class responsible for fetching
    and unpacking a source archive"""

    def __init__(self, archive):
        self.url = inary.uri.URI(archive.uri)
        self.archiveFile = os.path.join(
            ctx.config.archives_dir(), self.url.filename())
        self.archive = archive
        self.progress = None
        self.isgit = (self.url.get_uri().startswith("git://")
                      or self.url.get_uri().endswith(".git"))
        self.branch = "master"  # TODO need support branch from pspec

    def fetch(self, interactive=True):
        if not self.is_cached(interactive):
            if interactive:
                self.progress = ctx.ui.Progress

            try:
                ctx.ui.info(
                    _("Fetching source from: \"{}\"").format(
                        self.url.uri))
                if self.url.get_uri().startswith("mirrors://"):
                    self.fetch_from_mirror()
                elif self.url.get_uri().startswith("file://") or self.url.get_uri().startswith("/"):
                    self.fetch_from_locale()
                elif self.isgit:
                    self.branch = self.archive.sha1sum
                    inary.fetcher.fetch_git(
                        self.url, ctx.config.archives_dir()+"/"+self.url.filename(), self.branch)
                else:
                    inary.fetcher.fetch_url(
                        self.url, ctx.config.archives_dir(), self.progress)
            except inary.fetcher.FetchError:
                if ctx.config.values.build.fallback and not self.is_cached(
                        interactive=False):
                    self.fetch_from_fallback()
                else:
                    raise

            ctx.ui.info(
                _("Source archive is stored: \"{0}/{1}\"").format(
                    ctx.config.archives_dir(),
                    self.url.filename()))

    def fetch_from_fallback(self):
        inary.fetcher.fetch_url(
            self.url.get_uri(),
            ctx.config.archives_dir(),
            self.progress)

    def fetch_from_locale(self):
        inary.fetcher.fetch_from_locale(
            self.url.get_uri(),
            ctx.config.archives_dir(),
            destfile=self.url.filename())

    def fetch_from_mirror(self):
        inary.fetcher.fetch_from_mirror(
            self.url.get_uri(),
            ctx.config.archives_dir(),
            self.progress)

    def is_cached(self, interactive=True):

        if not os.access(self.archiveFile, os.R_OK):
            return False

        # check hash
        if util.check_file_hash(
                self.archiveFile,
                self.archive.sha1sum) or ctx.get_option('ignore_verify'):
            if interactive and ctx.config.get_option('debug'):
                ctx.ui.info(_('\"{}\" [cached]').format(self.archive.name))
            return True

        return False

    def unpack(self, target_dir, clean_dir=True):

        # check archive file's integrity
        if not util.check_file_hash(self.archiveFile, self.archive.sha1sum):
            ctx.ui.warning(_("Archive File: {}\n * Expected sha1 value: {}\n * Received sha1 value: {}\n".format(
                self.url.filename(), self.archive.sha1sum, util.sha1_file(self.archiveFile))))
            if not ctx.get_option('ignore_verify'):
                raise SourceArchiveError(_("unpack: check_file_hash failed."))
            else:
                ctx.ui.warning(
                    _("* Archive verification passed. Such problems may occur during the build process."))
        try:
            archive = Archive(self.archiveFile, self.archive.type)
        except UnknownArchiveType:
            raise SourceArchiveError(
                _("Unknown archive type '{0}' is given for '{1}'.").format(
                    self.archive.type, self.url.filename()))
        except ArchiveHandlerNotInstalled:
            raise SourceArchiveError(
                _("Inary needs \'{}\' to unpack this archive but it is not installed.").format(
                    self.archive.type))

        target_dir = os.path.join(target_dir, self.archive.target or "")
        archive.unpack(target_dir, clean_dir)
