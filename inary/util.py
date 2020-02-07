# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

"""misc. utility functions, including process and file utils"""

# standard python modules

import fcntl
import fnmatch
import hashlib
import operator
import os
import platform
import re
import shutil
import struct

import sys
import termios
import unicodedata

from functools import reduce

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

try:
    import subprocess
except ImportError:
    raise Exception(_("Module: \'subprocess\' can not imported."))


class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)

        return cls.instance


# inary modules
import inary
import inary.errors
import inary.context as ctx


class Error(inary.errors.Error):
    pass


class FileError(Error):
    pass


class FilePermissionDeniedError(Error):
    pass

def locked(func):
    """
    Decorator for synchronizing privileged functions
    """

    def wrapper(*__args, **__kw):
        try:
            lock = open(join_path(ctx.config.lock_dir(), 'inary'), 'w')
        except IOError:
            raise inary.errors.PrivilegeError(_("You have to be root for this operation."))

        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            ctx.locked = True
        except IOError:
            if not ctx.locked:
                raise inary.errors.AnotherInstanceError(
                    _("Another instance of Inary is running. Only one instance is allowed."))

        try:
            inary.db.invalidate_caches()
            ctx.ui.info(_('Invalidating database caches...'), verbose=True)
            ret = func(*__args, **__kw)
            ctx.ui.info(_('Updating database caches...'), verbose=True)
            inary.db.update_caches()
            return ret
        finally:
            ctx.locked = False
            lock.close()

    return wrapper


#########################
# string/list/functional#
#########################

whitespace = ' \t\n\r\v\f'
ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
ascii_letters = ascii_lowercase + ascii_uppercase
digits = '0123456789'
hexdigits = digits + 'abcdef' + 'ABCDEF'
octdigits = '01234567'
punctuation = """!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
printable = digits + ascii_letters + punctuation + whitespace


def every(pred, seq):
    return reduce(operator.and_, list(map(pred, seq)), True)


def any(pred, seq):
    return reduce(operator.or_, list(map(pred, seq)), False)


def unzip(seq):
    return list(zip(*seq))


def concat(l):
    """Concatenate a list of lists."""
    return reduce(operator.concat, l)


def multisplit(str, chars):
    """Split str with any of the chars."""
    l = [str]
    for c in chars:
        l = concat([x.split(c) for x in l])
    return l


def same(l):
    """Check if all elements of a sequence are equal."""
    if len(l) == 0:
        return True
    else:
        last = l.pop()
        for x in l:
            if x != last:
                return False
        return True


def any(pred, seq):
    return reduce(operator.or_, list(map(pred, seq)), False)


def flatten_list(l):
    """Flatten a list of lists."""
    # Fastest solution is list comprehension
    # See: http://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
    return [item for sublist in l for item in sublist]

def unique_list(l):
    """Creates a unique list by deleting duplicate items"""
    list_set = set(l)
    unique_list = (list(list_set))
    return [x for x in unique_list]

def strlist(l):
    """Concatenate string reps of l's elements."""
    return "".join([str(x) + ' ' for x in l])


def prefix(a, b):
    """Check if sequence a is a prefix of sequence b."""
    if len(a) > len(b):
        return False
    for i in range(0, len(a)):
        if a[i] != b[i]:
            return False
    return True


def remove_prefix(a, b):
    """Remove prefix a from sequence b."""
    assert prefix(a, b)
    return b[len(a):]


def suffix(a, b):
    """Check if sequence a is a suffix of sequence b."""
    if len(a) > len(b):
        return False
    for i in range(1, len(a) + 1):
        if a[-i] != b[-i]:
            return False
    return True


def remove_suffix(a, b):
    """Remove suffix a from sequence b."""
    assert suffix(a, b)
    return b[:-len(a)]


def human_readable_size(size=0):
    symbols, depth = [' B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'], 0

    while size > 1000 and depth < 8:
        size = float(size / 1024)
        depth += 1

    return size, symbols[depth]


def human_readable_rate(size=0):
    x = human_readable_size(size)
    return x[0], x[1] + '/s'


def format_by_columns(strings, sep_width=2):
    longest_str_len = len(max(strings, key=len))
    term_rows, term_columns = get_terminal_size()

    def get_columns(max_count):
        if longest_str_len > term_columns:
            return [longest_str_len]

        columns = []
        for name in strings:
            table_width = sum(columns) + len(name) + len(columns) * sep_width
            if table_width > term_columns:
                break

            columns.append(len(name))
            if len(columns) == max_count:
                break

        return columns

    def check_size(columns):
        total_sep_width = (len(columns) - 1) * sep_width

        for n, name in enumerate(strings):
            col = n % len(columns)
            if len(name) > columns[col]:
                columns[col] = len(name)

            if len(columns) > 1:
                width = sum(columns) + total_sep_width
                if width > term_columns:
                    return False

        return True

    columns = get_columns(term_columns)

    while not check_size(columns):
        columns = get_columns(len(columns) - 1)

    sep = " " * sep_width
    lines = []
    current_line = []
    for n, name in enumerate(strings):
        col = n % len(columns)
        current_line.append(name.ljust(columns[col]))

        if col == len(columns) - 1:
            lines.append(sep.join(current_line))
            current_line = []

    if current_line:
        lines.append(sep.join(current_line))

    return "\n".join(lines)


##############################
# Process Releated Functions #
##############################

def search_executable(executable):
    """Search for the executable in user's paths and return it."""
    for _path in os.environ["PATH"].split(":"):
        full_path = os.path.join(_path, executable)
        if os.path.exists(full_path) and os.access(full_path, os.X_OK):
            return full_path
    return None


def run_batch(cmd, ui_debug=True):
    """Run command and report return value and output."""
    ctx.ui.info(_('Running ') + cmd, verbose=True)
    p = subprocess.Popen(cmd, shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if ui_debug: ctx.ui.debug(_('return value for "{0}" is {1}').format(cmd, p.returncode))
    return p.returncode, out.decode('utf-8'), err

# TODO: it might be worthwhile to try to remove the
# use of ctx.stdout, and use run_batch()'s return
# values instead. but this is good enough :)
def run_logged(cmd):
    """Run command and get the return value."""
    ctx.ui.info(_('Running ') + cmd, verbose=True)
    if ctx.stdout:
        stdout = ctx.stdout
    else:
        if ctx.get_option('debug'):
            stdout = None
        else:
            stdout = subprocess.PIPE
    if ctx.stderr:
        stderr = ctx.stderr
    else:
        if ctx.get_option('debug'):
            stderr = None
        else:
            stderr = subprocess.STDOUT

    p = subprocess.Popen(cmd, shell=True, stdout=stdout, stderr=stderr)
    out, err = p.communicate()
    ctx.ui.debug(_('return value for "{0}" is {1}').format(cmd, p.returncode))

    return p.returncode


######################
# Terminal functions #
######################

def get_terminal_size():
    try:
        ret = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, "1234")
    except IOError:
        rows = int(os.environ.get("LINES", 25))
        cols = int(os.environ.get("COLUMNS", 80))
        return rows, cols

    return struct.unpack("hh", ret)


def xterm_title(message):
    """Set message as console window title."""
    if "TERM" in os.environ and sys.stderr.isatty():
        terminalType = os.environ["TERM"]
        for term in ["xterm", "Eterm", "aterm", "rxvt", "screen", "kterm", "rxvt-unicode"]:
            if terminalType.startswith(term):
                sys.stderr.write("\x1b]2;" + str(message) + "\x07")
                sys.stderr.flush()
                break


def xterm_title_reset():
    """Reset console window title."""
    if "TERM" in os.environ:
        xterm_title("")

#############################
#   ncurses like functions  #
#############################
def initscr():
    """Clear and create a window"""
    printw("\x1b[s\x1bc")

def endsrc():
    """Clear and restore screen"""
    printw("\x1bc\x1b[u")

def move(x,y):
    """Move"""
    printw("\x1b[{};{}f".format(y,x))

def printw(msg=''):
    """Print clone"""
    sys.stdout.write(msg)
    sys.stdout.flush()

def mvprintw(x,y,msg=''):
    """Move and print"""
    move(x,y)
    printw(msg)

def noecho(enabled=True):
    if(ctx.get_option('no_color')==False):
        if(enabled):
            printw("\x1b[?25l")
        else:
            printw("\x1b[?25h")

def attron(attribute):
    """Attribute enable"""
    if(attribute=="A_NORMAL"):
        sys.stdout.write("\x1b[;0m")
    elif(attribute=="A_UNDERLINE"):
        sys.stdout.write("\x1b[4m")
    elif(attribute=="A_REVERSE"):
        sys.stdout.write("\x1b[7m")
    elif(attribute=="A_BLINK"):
        sys.stdout.write("\x1b[5m")
    elif(attribute=="A_DIM"):
        sys.stdout.write("\x1b[2m")
    elif(attribute=="A_BOLD"):
        sys.stdout.write("\x1b[1m")
    elif(attribute=="A_INVIS"):
        sys.stdout.write("\x1b[8m")
    elif(attribute=="C_BLACK"):
        sys.stdout.write("\x1b[30m")
    elif(attribute=="C_RED"):
        sys.stdout.write("\x1b[31m")
    elif(attribute=="C_GREEN"):
        sys.stdout.write("\x1b[32m")
    elif(attribute=="C_YELLOW"):
        sys.stdout.write("\x1b[33m")
    elif(attribute=="C_BLUE"):
        sys.stdout.write("\x1b[34m")
    elif(attribute=="C_MAGENTA"):
        sys.stdout.write("\x1b[35m")
    elif(attribute=="C_CYAN"):
        sys.stdout.write("\x1b[36m")
    elif(attribute=="C_WHITE"):
        sys.stdout.write("\x1b374m")
    elif(attribute=="B_BLACK"):
        sys.stdout.write("\x1b[40m")
    elif(attribute=="B_RED"):
        sys.stdout.write("\x1b[41m")
    elif(attribute=="B_GREEN"):
        sys.stdout.write("\x1b[42m")
    elif(attribute=="B_YELLOW"):
        sys.stdout.write("\x1b[43m")
    elif(attribute=="B_BLUE"):
        sys.stdout.write("\x1b[44m")
    elif(attribute=="B_MAGENTA"):
        sys.stdout.write("\x1b[45m")
    elif(attribute=="B_CYAN"):
        sys.stdout.write("\x1b[46m")
    elif(attribute=="B_WHITE"):
        sys.stdout.write("\x1b[47m")
    sys.stdout.flush()

def drawbox(x1,y1,x2,y2):
    """Draw box"""
    mvprintw(x1,y1,"╔")
    mvprintw(x1,y2,"╚")
    mvprintw(x2,y1,"╗")
    mvprintw(x2,y2,"╝")
    for i in range((x1+1),(x2-1)):
        mvprintw(i,y1,"═")
        mvprintw(i,y2,"═")
    for i in range((y1+1),(y2-1)):
        mvprintw(x1,i,"║")
        mvprintw(x2,i,"║")

#############################
# Path Processing Functions #
#############################

def splitpath(a):
    """split path into components and return as a list
    os.path.split doesn't do what I want like removing trailing /"""
    comps = a.split(os.path.sep)
    if comps[len(comps) - 1] == '':
        comps.pop()
    return comps


def makepath(comps, relative=False, sep=os.path.sep):
    """Reconstruct a path from components."""
    path = reduce(lambda x, y: x + sep + y, comps, '')
    if relative:
        return path[len(sep):]
    else:
        return path


def parentpath(a, sep=os.path.sep):
    # remove trailing '/'
    a = a.rstrip(sep)
    return a[:a.rfind(sep)]


def parenturi(a):
    return parentpath(a, '/')


def subpath(a, b):
    """Find if path a is before b in the directory tree."""
    return prefix(splitpath(a), splitpath(b))


def removepathprefix(prefix, path):
    """Remove path prefix a from b, finding the pathname rooted at a."""
    comps = remove_prefix(splitpath(prefix), splitpath(path))
    if len(comps) > 0:
        return join_path(*tuple(comps))
    else:
        return ""


def join_path(a, *p):
    """Join two or more pathname components.
    Python os.path.join cannot handle '/' at the start of latter components.
    """
    path = a
    for b in p:
        b = b.lstrip('/')
        if path == '' or path.endswith('/'):
            path += b
        else:
            path += '/' + b
    return path


####################################
# File/Directory Related Functions #
####################################

def check_file(_file, mode=os.F_OK):
    """Shorthand to check if a file exists."""
    if not os.access(_file, mode):
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

    if os.path.exists(_dir) and (not os.path.isdir(_dir) and not os.path.islink(_dir)):
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
            raise FilePermissionDeniedError(_("You don't have necessary read permissions"))
        else:
            raise FileError(_("Cannot calculate SHA1 hash of \"{}\"").format(filename))


def sha1_data(data):
    """Calculate sha1 hash of given data."""
    m = hashlib.sha1()
    m.update(data.encode('utf-8'))
    return m.hexdigest()


def uncompress(patchFile, compressType="gz", targetDir=""):
    """Uncompress the file and return the new path."""
    formats = ("gz", "gzip", "bz2", "bzip2", "lzma", "xz")
    if compressType not in formats:
        raise Error(_("Compression type is not valid: '{}'").format(compressType))

    archive = inary.archive.Archive(patchFile, compressType)
    try:
        archive.unpack(targetDir)
    except Exception as msg:
        raise Error(_("Error while decompressing \"{0}\": {1}").format(patchFile, msg))

    # FIXME: Get file path from Archive instance
    filePath = join_path(targetDir, os.path.basename(patchFile))

    # remove suffix from file cause its uncompressed now
    extensions = {"gzip": "gz", "bzip2": "bz2"}
    extension = extensions.get(compressType, compressType)
    return filePath.split(".{}".format(extension))[0]


def check_patch_level(workdir, path):
    level = 0
    while path:
        if os.path.isfile("{0}/{1}".format(workdir, path)): return level
        if path.find("/") == -1: return None
        level += 1
        path = path[path.find("/") + 1:]


def do_patch(sourceDir, patchFile, level=0, name=None, reverse=False):
    """Apply given patch to the sourceDir."""
    cwd = os.getcwd()
    if os.path.exists(sourceDir):
        os.chdir(sourceDir)
    else:
        raise Error(_("ERROR: WorkDir ({}) does not exist\n").format(sourceDir))

    check_file(patchFile)

    if level is None:
        with open(patchFile) as patchfile:
            lines = patchfile.readlines()
            try:
                paths_m = [l.strip().split()[1] for l in lines if l.startswith("---") and "/" in l]
                try:
                    paths_p = [l.strip().split()[1] for l in lines if l.startswith("+++")]
                except IndexError:
                    paths_p = []
            except IndexError:
                pass
            else:
                if not paths_p:
                    paths_p = paths_m[:]
                    try:
                        paths_m = [l.strip().split()[1] for l in lines if l.startswith("***") and "/" in l]
                    except IndexError:
                        pass

                for path_p, path_m in zip(paths_p, paths_m):
                    if "/dev/null" in path_m and not len(paths_p) - 1 == paths_p.index(path_p): continue
                    level = check_patch_level(sourceDir, path_p)
                    if level is None and len(paths_m) - 1 == paths_m.index(path_m):
                        level = check_patch_level(sourceDir, path_m)
                    if not level is None:
                        ctx.ui.info(_("Detected patch level={0} for {1}").format(level, os.path.basename(patchFile)), verbose=True)
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
            raise Error(_("ERROR: patch (\"{0}\") failed: {1}").format(patchFile, out))

    os.chdir(cwd)


def strip_file(filepath, fileinfo, outpath):
    """Strip an elf file from debug symbols."""

    def run_strip(f, flags=""):
        p = os.popen("strip {0} {1}".format(flags, f))
        ret = p.close()
        if ret:
            ctx.ui.warning(_("\'strip\' command failed for file \"{}\"!").format(f))

    def run_chrpath(f):
        """ remove rpath info from binary """
        p = os.popen("chrpath -d {}".format(f))
        ret = p.close()
        if ret:
            ctx.ui.warning(_("\'chrpath\' command failed for file \"{}\"!").format(f))

    def save_elf_debug(f, o):
        """copy debug info into file.debug file"""
        p = os.popen("objcopy --only-keep-debug {0} {1}{2}".format(f, o, ctx.const.debug_file_suffix))
        ret = p.close()
        if ret:
            ctx.ui.warning(_("\'objcopy\' (keep-debug) command failed for file \"{}\"!").format(f))

        """mark binary/shared objects to use file.debug"""
        p = os.popen("objcopy --add-gnu-debuglink={0}{1} {2}".format(o, ctx.const.debug_file_suffix, f))
        ret = p.close()
        if ret:
            ctx.ui.warning(_("\'objcopy\' (add-debuglink) command failed for file \"{}\"!").format(f))


    if "current ar archive" in fileinfo:
        run_strip(filepath, "--strip-debug")
        return True

    elif re.search("SB\s+executable", fileinfo):
        if ctx.config.values.build.generatedebug:
            ensure_dirs(os.path.dirname(outpath))
            save_elf_debug(filepath, outpath)
        run_strip(filepath)
        # FIXME: removing RPATH also causes problems, for details see gelistirici mailing list - caglar10ur
        # run_chrpath(filepath)
        return True

    elif re.search("SB\s+shared object", fileinfo):
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


########################################
# Package/Repository Related Functions #
########################################

def package_filename(name, version, release, distro_id=None, arch=None):
    """Return a filename for a package with the given information. """

    if distro_id is None:
        distro_id = ctx.config.values.general.distribution_id

    if arch is None:
        arch = ctx.config.values.general.architecture

    fn = "-".join((name, version, release, distro_id, arch))
    fn += ctx.const.package_suffix

    return fn


def parse_package_name_legacy(package_name):
    """Separate package name and version string for package formats <= 1.1.

    example: tasma-1.0.3-5-2 -> (tasma, 1.0.3-5-2)
    """
    # We should handle package names like 855resolution
    name = []
    for part in package_name.split("-"):
        if name != [] and part[0] in digits:
            break
        else:
            name.append(part)
    name = "-".join(name)
    version = package_name[len(name) + 1:]

    return name, version


def parse_package_name(package_name):
    """Separate package name and version string.

    example: tasma-1.0.3-5-p11-x86_64 -> (tasma, 1.0.3-5)
    """

    # Strip extension if exists
    if package_name.endswith(ctx.const.package_suffix):
        package_name = remove_suffix(ctx.const.package_suffix, package_name)

    try:
        name, version, release, distro_id, arch = package_name.rsplit("-", 4)

        # Arch field cannot start with a digit. If a digit is found,
        # the package might have an old format. Raise here to call
        # the legacy function.
        if not arch or arch[0] in digits:
            raise ValueError

    except ValueError:
        try:
            return parse_package_name_legacy(package_name)
        except:
            raise Error(_("Invalid package name: \"{}\"").format(package_name))

    return name, "{0}-{1}".format(version, release)


def parse_package_dir_path(package_name):
    name = parse_package_name(package_name)[0]
    if name.split("-").pop() in ["devel", "32bit", "doc", "docs", "pages", "static", "dbginfo", "32bit-dbginfo",
                                 "userspace"]: name = name[:-1 - len(name.split("-").pop())]
    return "{0}/{1}".format(name[0:4].lower() if name.startswith("lib") and len(name) > 3 else name.lower()[0],
                            name.lower())


def parse_delta_package_name_legacy(package_name):
    """Separate delta package name and release infos for package formats <= 1.1.

    example: tasma-5-7.delta.inary -> (tasma, 5, 7)
    """
    name, build = parse_package_name(package_name)
    build = build[:-len(ctx.const.delta_package_suffix)]
    buildFrom, buildTo = build.split("-")

    return name, buildFrom, buildTo


def parse_delta_package_name(package_name):
    """Separate delta package name and release infos

    example: tasma-5-7-p11-x86_64.delta.inary -> (tasma, 5, 7)
    """

    # Strip extension if exists
    if package_name.endswith(ctx.const.delta_package_suffix):
        package_name = remove_suffix(ctx.const.delta_package_suffix,
                                     package_name)

    try:
        name, source_release, target_release, distro_id, arch = \
            package_name.rsplit("-", 4)

        # Arch field cannot start with a digit. If a digit is found,
        # the package might have an old format. Raise here to call
        # the legacy function.
        if not arch or arch[0] in digits:
            raise ValueError

    except ValueError:
        try:
            return parse_delta_package_name_legacy(package_name)
        except:
            raise Error(_("Invalid delta package name: \"{}\"").format(package_name))

    return name, source_release, target_release


def split_package_filename(filename):
    """Split fields in package filename.

    example: tasma-1.0.3-5-p11-x86_64.inary -> (tasma, 1.0.3, 5, p11, x86_64)
    """

    # Strip extension if exists
    if filename.endswith(ctx.const.package_suffix):
        filename = remove_suffix(ctx.const.package_suffix, filename)

    try:
        name, version, release, distro_id, arch = filename.rsplit("-", 4)

        # Arch field cannot start with a digit. If a digit is found,
        # the package might have an old format.
        if not arch or arch[0] in digits:
            raise ValueError

    except ValueError:
        name, version = parse_package_name_legacy(filename)
        version, release, build = split_version(version)
        distro_id = arch = None

    return name, version, release, distro_id, arch


def split_delta_package_filename(filename):
    """Split fields in delta package filename.

    example: tasma-5-7-p11-x86_64.delta.inary -> (tasma, 5, 7, p11, x86-64)
    """

    # Strip extension if exists
    if filename.endswith(ctx.const.delta_package_suffix):
        filename = remove_suffix(ctx.const.delta_package_suffix, filename)

    try:
        name, source_release, target_release, distro_id, arch = \
            filename.rsplit("-", 4)

        # Arch field cannot start with a digit. If a digit is found,
        # the package might have an old format.
        if not arch or arch[0] in digits:
            raise ValueError

    except ValueError:
        # Old formats not supported
        name = parse_delta_package_name_legacy(filename)[0]
        source_release = target_release = None

    return name, source_release, target_release, distro_id, arch


def split_version(package_version):
    """Split version, release and build parts of a package version

    example: 1.0.3-5-2 -> (1.0.3, 5, 2)
    """
    version, sep, release_and_build = package_version.partition("-")
    release, sep, build = release_and_build.partition("-")
    return version, release, build


def filter_latest_packages(package_paths):
    """ For a given inary package paths list where there may also be multiple versions
        of the same package, filters only the latest versioned ones """

    import inary.version

    latest = {}
    for path in package_paths:

        name, version = parse_package_name(os.path.basename(path[:-len(ctx.const.package_suffix)]))

        if name in latest:
            l_version, l_release, l_build = split_version(latest[name][1])
            r_version, r_release, r_build = split_version(version)

            try:
                l_release = int(l_release)
                r_release = int(r_release)

                l_build = int(l_build) if l_build else None
                r_build = int(r_build) if r_build else None

            except ValueError:
                continue

            if l_build and r_build:
                if l_build > r_build:
                    continue

            elif l_release > r_release:
                continue

            elif l_release == r_release:
                l_version = inary.version.make_version(l_version)
                r_version = inary.version.make_version(r_version)

                if l_version > r_version:
                    continue

        if version:
            latest[name] = (path, version)

    return [x[0] for x in list(latest.values())]


def colorize(msg, color):
    """Colorize the given message for console output"""
    if color in ctx.const.colors and not ctx.get_option('no_color'):
        return str(ctx.const.colors[color] + msg + ctx.const.colors['default'])
    else:
        return str(msg)


def config_changed(config_file):
    fpath = join_path(ctx.config.dest_dir(), config_file.path)
    if os.path.exists(fpath) and not os.path.isdir(fpath):
        if os.path.islink(fpath):
            f = os.readlink(fpath)
            if os.path.exists(f) and sha1_data(f) != config_file.hash:
                return True
        else:
            if sha1_file(fpath) != config_file.hash:
                return True
    return False


# recursively remove empty dirs starting from dirpath
def rmdirs(dirpath):
    if os.path.isdir(dirpath) and not os.listdir(dirpath):
        ctx.ui.info(_("Removing empty dir: \"{}\"").format(dirpath),verbose=True)
        os.rmdir(dirpath)
        rmdirs(os.path.dirname(dirpath))


# Python regex sucks
# http://mail.python.org/pipermail/python-list/2009-January/523704.html
def letters():
    start = end = None
    result = []
    for index in range(sys.maxunicode + 1):
        c = chr(index)
        if unicodedata.category(c)[0] == 'L':
            if start is None:
                start = end = c
            else:
                end = c
        elif start:
            if start == end:
                result.append(start)
            else:
                result.append(start + "-" + end)
            start = None
    return ''.join(result)


def get_kernel_option(option):
    """Get a dictionary of args for the given kernel command line option"""

    args = {}

    try:
        cmdline = open("/proc/cmdline").read().split()
    except IOError:
        return args

    for cmd in cmdline:
        if "=" in cmd:
            optName, optArgs = cmd.split("=", 1)
        else:
            optName = cmd
            optArgs = ""

        if optName == option:
            for arg in optArgs.split(","):
                if ":" in arg:
                    k, v = arg.split(":", 1)
                    args[k] = v
                else:
                    args[arg] = ""

    return args

def get_cpu_count():
    """
    This function part of portage
    Copyright 2015 Gentoo Foundation
    Distributed under the terms of the GNU General Public License v2

    Using:
    Try to obtain the number of CPUs available.
    @return: Number of CPUs or None if unable to obtain.
    """
    try:
        import multiprocessing
        return multiprocessing.cpu_count()
    except (ImportError, NotImplementedError):
        return None


def get_vm_info():
    vm_info = {}

    if platform.system() == 'Linux':
        try:
            proc = subprocess.Popen(["free"],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
        except OSError:
            pass
        output = proc.communicate()[0].decode('utf-8')
        if proc.wait() == os.EX_OK:
            for line in output.splitlines():
                line = line.split()
                if len(line) < 2:
                    continue
                if line[0] == "Mem:":
                    try:
                        vm_info["ram.total"] = int(line[1]) * 1024
                    except ValueError:
                        pass
                    if len(line) > 3:
                        try:
                            vm_info["ram.free"] = int(line[3]) * 1024
                        except ValueError:
                            pass
                elif line[0] == "Swap:":
                    try:
                        vm_info["swap.total"] = int(line[1]) * 1024
                    except ValueError:
                        pass
                    if len(line) > 3:
                        try:
                            vm_info["swap.free"] = int(line[3]) * 1024
                        except ValueError:
                            pass
    else:
        try:
            proc = subprocess.Popen(["sysctl", "-a"],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
        except OSError:
            pass
        else:
            output = proc.communicate()[0].decode('utf-8')
            if proc.wait() == os.EX_OK:
                for line in output.splitlines():
                    line = line.split(":", 1)
                    if len(line) != 2:
                        continue
