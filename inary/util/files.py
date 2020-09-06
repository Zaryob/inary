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

"""misc. utility functions, including process and file utils"""

from inary.errors import FileError, FilePermissionDeniedError, Error
from inary.util.strings import remove_prefix
from inary.util.process import run_batch
from inary.util.path import join_path
import fnmatch
import hashlib
import shutil
import os
import re

# Inary Modules
import inary
import inary.errors
import inary.context as ctx

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


####################################
# File/Directory Related Functions #
####################################


def check_file(_file, mode=os.F_OK, noerr=False):
    """Shorthand to check if a file exists."""
    if not os.access(_file, mode):
        if noerr:
            return False
        else:
            raise FileError(_("File {} not found.").format(_file))
    return True


def ensure_dirs(path):
    """Make sure the given directory path exists."""
    if not os.path.exists(path):
        os.makedirs(path)


def clean_dir(path):
    """Remove all content of a directory."""
    if os.path.exists(path):
        shutil.rmtree(path)


def delete_file(path):
    if os.path.isfile(path):
        if os.path.exists(path):
            os.remove(path)


def creation_time(_file):
    """Return the creation time of the given file."""
    if check_file(_file):
        import time
        st = os.stat(_file)
        return time.localtime(st.st_ctime)


def dir_size(_dir):
    """Calculate the size of files under a directory."""
    # It's really hard to give an approximate value for package's
    # installed size. Gettin a sum of all files' sizes if far from
    # being true. Using 'du' command (like Debian does) can be a
    # better solution :(.
    # Not really, du calculates size on disk, this is much better

    if os.path.exists(_dir) and (not os.path.isdir(_dir)
                                 and not os.path.islink(_dir)):
        # so, this is not a directory but file..
        return os.path.getsize(_dir)

    if os.path.islink(_dir):
        return int(len(read_link(_dir)))

    def sizes():
        for root, dirs, files in os.walk(_dir):
            yield sum(
                [os.path.getsize(join_path(root, name)) for name in files if not os.path.islink(join_path(root, name))])

    return sum(sizes())


def copy_file(src, dest):
    """Copy source file to the destination file."""
    check_file(src)
    ensure_dirs(os.path.dirname(dest))
    shutil.copyfile(src, dest)


def copy_file_stat(src, dest):
    """Copy source file to the destination file with all stat info."""
    check_file(src)
    ensure_dirs(os.path.dirname(dest))
    shutil.copy2(src, dest)


def free_space(directory=None):
    """Returns the free space (x Byte) in the device. """
    if not directory:
        # Defaults to /
        directory = ctx.config.values.general.destinationdirectory
    _stat = os.statvfs(directory)
    free_space = _stat.f_bfree * _stat.f_bsize

    return free_space


def read_link(link):
    """Return the normalized path which is pointed by the symbolic link."""
    # tarfile module normalizes the paths pointed by symbolic links. This
    # causes problems as the file hashes and sizes are calculated before
    # this normalization.
    return os.path.normpath(os.readlink(link))


def is_ar_file(file_path):
    return open(file_path, 'rb').read(8) == '!<arch>\n'


def clean_ar_timestamps(ar_file):
    """Zero all timestamps in the ar files."""
    if not is_ar_file(ar_file):
        return
    content = open(ar_file).readlines()
    fp = open(ar_file, 'w')
    for line in content:
        pos = line.rfind(chr(32) + chr(96))
        if pos > -1 and line[pos - 57:pos + 2].find(chr(47)) > -1:
            line = line[:pos - 41] + '0000000000' + line[pos - 31:]
        fp.write(line)
    fp.close()


def calculate_hash(path):
    """Return a (path, hash) tuple for given path."""
    if os.path.islink(path):
        # For symlinks, path string is hashed instead of the content
        value = sha1_data(read_link(path))
        if not os.path.exists(path):
            ctx.ui.info(_("Including external link \"{}\"").format(path))
    elif os.path.isdir(path):
        ctx.ui.info(_("Including directory \"{}\"").format(path))
        value = None
    else:
        if path.endswith('.a'):
            # .a file content changes with each compile due to timestamps
            # We pad them with zeroes, thus hash will be stable
            clean_ar_timestamps(path)
        value = sha1_file(path)

    return path, value


def get_file_hashes(top, excludePrefix=None, removePrefix=None):
    """Yield (path, hash) tuples for given directory tree.

    Generator function iterates over a toplevel path and returns the
    (filePath, sha1Hash) tuples for all files. If excludePrefixes list
    is given as a parameter, function will exclude the filePaths
    matching those prefixes. The removePrefix string parameter will be
    used to remove prefix from filePath while matching excludes, if
    given.
    """

    def is_included(path):
        if excludePrefix:
            temp = remove_prefix(removePrefix, path)
            while temp != "/":
                if len([x for x in excludePrefix if fnmatch.fnmatch(temp, x)]) > 0:
                    return False
                temp = os.path.dirname(temp)
        return True

    # single file/symlink case
    if not os.path.isdir(top) or os.path.islink(top):
        if is_included(top):
            yield calculate_hash(top)
        return

    for root, dirs, files in os.walk(top):
        # Hash files and file symlinks
        for name in files:
            path = os.path.join(root, name)
            if is_included(path):
                yield calculate_hash(path)

        # Hash symlink dirs
        # os.walk doesn't enter them, we don't want to follow them either
        # but their name and hashes must be reported
        # Discussed in bug #339
        for name in dirs:
            path = os.path.join(root, name)
            if os.path.islink(path):
                if is_included(path):
                    yield calculate_hash(path)

        # Hash empty dir
        # Discussed in bug #340
        if len(files) == 0 and len(dirs) == 0:
            if is_included(root):
                yield calculate_hash(root)


def check_file_hash(filename, hash):
    """Check the file's integrity with a given hash."""
    if os.path.isdir(filename+"/.git"):
        return True
    return sha1_file(filename) == hash


def sha1_file(filename):
    """Calculate sha1 hash of file."""
    # Broken links can cause problem!
    try:
        m = hashlib.sha1()
        f = open(filename, 'rb')
        while True:
            # 256 KB seems ideal for speed/memory tradeoff
            # It wont get much faster with bigger blocks, but
            # heap peak grows
            block = f.read(256 * 1024)
            if len(block) == 0:
                # end of file
                break
            m.update(block)
            # Simple trick to keep total heap even lower
            # Delete the previous block, so while next one is read
            # we wont have two allocated blocks with same size
            del block
        return m.hexdigest()
    except IOError as e:
        if e.errno == 13:
            # Permission denied, the file doesn't have read permissions, skip
            raise FilePermissionDeniedError(
                _("You don't have necessary read permissions"))
        else:
            raise FileError(
                _("Cannot calculate SHA1 hash of \"{}\"").format(filename))


def sha1_data(data):
    """Calculate sha1 hash of given data."""
    m = hashlib.sha1()
    m.update(data.encode('utf-8'))
    return m.hexdigest()


def uncompress(patchFile, compressType="gz", targetDir=""):
    """Uncompress the file and return the new path."""
    formats = ("gz", "gzip", "bz2", "bzip2", "lzma", "xz")
    if compressType not in formats:
        raise Error(
            _("Compression type is not valid: '{}'").format(compressType))

    archive = inary.archive.Archive(patchFile, compressType)
    try:
        archive.unpack(targetDir)
    except Exception as msg:
        raise Error(
            _("Error while decompressing \"{0}\": {1}").format(
                patchFile, msg))

    # FIXME: Get file path from Archive instance
    filePath = join_path(targetDir, os.path.basename(patchFile))

    # remove suffix from file cause its uncompressed now
    extensions = {"gzip": "gz", "bzip2": "bz2"}
    extension = extensions.get(compressType, compressType)
    return filePath.split(".{}".format(extension))[0]


def check_patch_level(workdir, path):
    level = 0
    while path:
        if os.path.isfile("{0}/{1}".format(workdir, path)):
            return level
        if path.find("/") == -1:
            return None
        level += 1
        path = path[path.find("/") + 1:]


def do_patch(sourceDir, patchFile, level=0, name=None, reverse=False):
    """Apply given patch to the sourceDir."""
    cwd = os.getcwd()
    if os.path.exists(sourceDir):
        os.chdir(sourceDir)
    else:
        raise Error(
            _("ERROR: WorkDir ({}) does not exist\n").format(sourceDir))

    check_file(patchFile)

    if level is None:
        with open(patchFile) as patchfile:
            lines = patchfile.readlines()
            try:
                paths_m = [l.strip().split()[1]
                           for l in lines if l.startswith("---") and "/" in l]
                try:
                    paths_p = [l.strip().split()[1]
                               for l in lines if l.startswith("+++")]
                except IndexError:
                    paths_p = []
            except IndexError:
                pass
            else:
                if not paths_p:
                    paths_p = paths_m[:]
                    try:
                        paths_m = [l.strip().split()[1]
                                   for l in lines if l.startswith("***") and "/" in l]
                    except IndexError:
                        pass

                for path_p, path_m in zip(paths_p, paths_m):
                    if "/dev/null" in path_m and not len(
                            paths_p) - 1 == paths_p.index(path_p):
                        continue
                    level = check_patch_level(sourceDir, path_p)
                    if level is None and len(
                            paths_m) - 1 == paths_m.index(path_m):
                        level = check_patch_level(sourceDir, path_m)
                    if not level is None:
                        ctx.ui.info(
                            _("Detected patch level={0} for {1}").format(
                                level, os.path.basename(patchFile)), verbose=True)
                        break

    if level is None:
        level = 0

    if name is None:
        name = os.path.basename(patchFile)

    if ctx.get_option('use_quilt'):
        patchesDir = join_path(sourceDir, ctx.const.quilt_dir_suffix)
        # Make sure sourceDir/patches directory exists and if not create one!
        if not os.path.exists(patchesDir):
            os.makedirs(patchesDir)
        # Import original patch into quilt tree
        (ret, out, err) = run_batch(
            'quilt import {0} -p {1} -P {2} \"{3}\"'.format(("-R" if reverse else ""), level, name, patchFile))
        # run quilt push to apply original patch into tree
        (ret, out, err) = run_batch('quilt push')
    else:
        # run GNU patch to apply original patch into tree
        (ret, out, err) = run_batch(
            "patch --remove-empty-files --no-backup-if-mismatch {0} -p{1} -i \"{2}\"".format(("-R" if reverse else ""),
                                                                                             level, patchFile))

    if ret:
        if out is None and err is None:
            # Which means stderr and stdout directed so they are None
            raise Error(_("ERROR: patch (\"{}\") failed.").format(patchFile))
        else:
            raise Error(
                _("ERROR: patch (\"{0}\") failed: {1}").format(
                    patchFile, out))

    os.chdir(cwd)


def strip_file(filepath, fileinfo, outpath):
    """Strip an elf file from debug symbols."""

    def run_strip(f, flags=""):
        p = os.popen("strip {0} {1}".format(flags, f))
        ret = p.close()
        if ret:
            ctx.ui.warning(
                _("\'strip\' command failed for file \"{}\"!").format(f))

    def run_chrpath(f):
        """ remove rpath info from binary """
        p = os.popen("chrpath -d {}".format(f))
        ret = p.close()
        if ret:
            ctx.ui.warning(
                _("\'chrpath\' command failed for file \"{}\"!").format(f))

    def save_elf_debug(f, o):
        """copy debug info into file.debug file"""
        p = os.popen(
            "objcopy --only-keep-debug {0} {1}{2}".format(f, o, ctx.const.debug_file_suffix))
        ret = p.close()
        if ret:
            ctx.ui.warning(
                _("\'objcopy\' (keep-debug) command failed for file \"{}\"!").format(f))

        """mark binary/shared objects to use file.debug"""
        p = os.popen(
            "objcopy --add-gnu-debuglink={0}{1} {2}".format(o, ctx.const.debug_file_suffix, f))
        ret = p.close()
        if ret:
            ctx.ui.warning(
                _("\'objcopy\' (add-debuglink) command failed for file \"{}\"!").format(f))

    if "current ar archive" in fileinfo:
        run_strip(filepath, "--strip-debug")
        return True

    elif re.search(r"SB\s+executable", fileinfo):
        if ctx.config.values.build.generatedebug:
            ensure_dirs(os.path.dirname(outpath))
            save_elf_debug(filepath, outpath)
        run_strip(filepath)
        # FIXME: removing RPATH also causes problems, for details see gelistirici mailing list - caglar10ur
        # run_chrpath(filepath)
        return True

    elif re.search(r"SB\s+shared object", fileinfo):
        if ctx.config.values.build.generatedebug:
            ensure_dirs(os.path.dirname(outpath))
            save_elf_debug(filepath, outpath)
        run_strip(filepath, "--strip-unneeded")
        # run_chrpath(filepath)
        # FIXME: warn for TEXTREL
        return True

    return False


def partition_freespace(directory):
    """Return free space of given directory's partition."""
    st = os.statvfs(directory)
    return st.f_frsize * st.f_bfree
