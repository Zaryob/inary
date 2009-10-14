# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# misc. utility functions, including process and file utils

# Authors:  Eray Ozkural <eray@uludag.org.tr>
#           Baris Metin <baris@uludag.org.tr>
#           S. Caglar Onur <caglar@uludag.org.tr>
#           A. Murat Eren <meren@uludag.org.tr>

# standard python modules
import os
import sys
import sha
import shutil
import statvfs

# pisi modules
import pisi
import pisi.context as ctx

class FileError(pisi.Error):
    pass

class UtilError(pisi.Error):
    pass


#########################
# spec validation utility #
#########################

class Checks:
    def __init__(self):
        self.list = None
    
    def add(self, err):
        if not self.list:
            self.list = []
        self.list.append(err)
    
    def join(self, list):
        if list != None:
            if not self.list:
                self.list = []
            self.list.extend(list)
    
    def has_tag(self, var, section, name):
        if not var:
            if not self.list:
                self.list = []
            self.list.append("%s section should have a '%s' tag" % (section, name))


#########################
# string/list functions #
#########################

def unzip(seq):
    return zip(*seq)

def concat(l):
    '''concatenate a list of lists'''
    return reduce( lambda x,y: x+y, l )

def strlist(l):
    """concatenate string reps of l's elements"""
    return "".join(map(lambda x: str(x) + ' ', l))

def multisplit(str, chars):
    """ split str with any of chars"""
    l = [str]
    for c in chars:
        l = concat(map(lambda x:x.split(c), l))
    return l

def same(l):
    '''check if all elements of a sequence are equal'''
    if len(l)==0:
        return True
    else:
        last = l.pop()
        for x in l:
            if x!=last:
                return False
        return True

def prefix(a, b):
    '''check if sequence a is a prefix of sequence b'''
    if len(a)>len(b):
        return False
    for i in range(0,len(a)):
        if a[i]!=b[i]:
            return False
    return True

def remove_prefix(a,b):
    "remove prefix a from sequence b"
    assert prefix(a,b)
    return b[len(a):]


##############################
# Process Releated Functions #
##############################

def run_batch(cmd):
    """run command non-interactively and report return value and output"""
    ui.info('running ' + cmd)
    a = os.popen(cmd)
    lines = a.readlines()
    ret = a.close()
    ui.debug('return value ' + ret)
    successful = ret == None
    if not successful:
      ui.error('ERROR: executing command: ' + cmd + '\n' + strlist(lines))
    return (successful,lines)


def xterm_title(message):
    """sets message as a console window's title"""
    if os.environ.has_key("TERM") and sys.stderr.isatty():
        terminalType = os.environ["TERM"]
        for term in ["xterm", "Eterm", "aterm", "rxvt", "screen", "kterm", "rxvt-unicode"]:
            if terminalType.startswith(term):
                sys.stderr.write("\x1b]2;"+str(message)+"\x07")
                sys.stderr.flush()
                break

def xterm_title_reset():
    """resets console window's title"""
    if os.environ.has_key("TERM"):
        terminalType = os.environ["TERM"]
        xterm_title(os.environ["TERM"])

#############################
# Path Processing Functions #
#############################

def splitpath(a):
    """split path into components and return as a list
    os.path.split doesn't do what I want like removing trailing /"""
    comps = a.split(os.path.sep)
    if comps[len(comps)-1]=='':
        comps.pop()
    return comps

# I'm not sure how necessary this is. Ahem.
def commonprefix(l):
    """an improved version of os.path.commonprefix,
    returns a list of path components"""
    common = []
    comps = map(splitpath, l)
    for i in range(0, min(len,l)):
        compi = map(lambda x: x[i], comps) # get ith slice
        if same(compi):
            common.append(compi[0])
    return common

# but this one is necessary
def subpath(a, b):
    "find if path a is before b in the directory tree"
    return prefix(splitpath(a), splitpath(b))

def removepathprefix(prefix, path):
    "remove path prefix a from b, finding the pathname rooted at a"
    comps = remove_prefix(splitpath(prefix), splitpath(path))
    if len(comps) > 0:
        return os.path.join(*tuple(comps))
    else:
        return ""

def absolute_path(path):
    "determine if given @path is absolute"
    comps = splitpath(path)
    return comps[0] == ''

####################################
# File/Directory Related Functions #
####################################

def check_file(file, mode = os.F_OK):
    "shorthand to check if a file exists"
    if not os.access(file, mode):
        raise FileError("File " + file + " not found")
    return True

def check_dir(dir):
    """check if directory exists, and create if it doesn't.
    works recursively"""
    dir = dir.strip().rstrip("/")
    if not os.access(dir, os.F_OK):
        os.makedirs(dir)

def clean_dir(path):
    "Remove all content of a directory (top)"
    # don't reimplement the wheel
    if os.path.exists(path):
        shutil.rmtree(path)

def dir_size(dir):
    """ calculate the size of files under a dir
    based on the os module example"""
    # It's really hard to give an approximate value for package's
    # installed size. Gettin a sum of all files' sizes if far from
    # being true. Using 'du' command (like Debian does) can be a
    # better solution :(.
    getsize = os.path.getsize
    join = os.path.join
    islink = os.path.islink
    def sizes():
        for root, dirs, files in os.walk(dir):
            yield sum([getsize(join(root, name)) for name in files if not islink(join(root,name))])
    return sum( sizes() )

def copy_file(src,dest):
    """copy source file to destination file"""
    check_file(src)
    check_dir(os.path.dirname(dest))
    shutil.copyfile(src, dest)

def get_file_hashes(top, exclude_prefix=None, removePrefix=None):
    """Generator function iterates over a toplevel path and returns the
    (filePath, sha1Hash) tuple for all files. If excludePrefixes list
    is given as a parameter, function will exclude the filePaths
    matching those prefixes. The removePrefix string parameter will be
    used to remove prefix from filePath while matching excludes, if
    given."""

    # also handle single files
    if os.path.isfile(top):
        yield (top, sha1_file(top))
        return

    def has_excluded_prefix(filename):
        if exclude_prefix and removePrefix:
            tempfnam = remove_prefix(removePrefix, filename)
            for p in exclude_prefix:
                if tempfnam.startswith(p):
                    return 1
                else:
                    return 0
        return 0

    for root, dirs, files in os.walk(top, topdown=False):
        #bug 339
        if os.path.islink(root) and not has_excluded_prefix(root):
            #yield the symlink..
            #bug 373
            yield (root, sha1_data(os.readlink(root)))
            exclude_prefix.append(remove_prefix(removePrefix, root) + "/")
            continue

        #bug 397
        for dir in dirs:
            d = os.path.join(root, dir)
            if os.path.islink(d) and not has_excluded_prefix(d):
                yield (d, sha1_data(os.readlink(d)))
                exclude_prefix.append(remove_prefix(removePrefix, d) + "/")

        #bug 340
        if os.path.isdir(root) and not has_excluded_prefix(root):
            parent, r, d, f = root, '', '', ''
            for r, d, f in os.walk(parent, topdown=False): pass
            if not f and not d:
                yield (parent, sha1_file(parent))

        for fname in files:
            f = os.path.join(root, fname)
            if has_excluded_prefix(f):
                continue
            #bug 373
            elif os.path.islink(f):
                yield (f, sha1_data(os.readlink(f)))
            else:
                yield (f, sha1_file(f))

def copy_dir(src, dest):
    """copy source dir to destination dir recursively"""
    shutil.copytree(src, dest)

def check_file_hash(filename, hash):
    """Check the files integrity with a given hash"""
    if sha1_file(filename) == hash:
        return True

    return False

def sha1_file(filename):
    """calculate sha1 hash of filename"""
    # Broken links can cause problem!
    try:
        m = sha.new()
        f = file(filename, 'rb')
        for line in f:
            m.update(line)
        return m.hexdigest()
    except IOError:
        return "0" 

def sha1_data(data):
    """calculate sha1 hash of given data"""
    try:
        m = sha.new()
        m.update(data)
        return m.hexdigest()
    except:
        return "0" 

def uncompress(patchFile, compressType="gz", targetDir=None):
    """uncompresses a file and returns the path of the uncompressed
    file"""
    if targetDir:
        filePath = os.path.join(targetDir,
                                os.path.basename(patchFile))
    else:
        filePath = os.path.basename(patchFile)

    if compressType == "gz":
        from gzip import GzipFile
        obj = GzipFile(patchFile)
    elif compressType == "bz2":
        from bz2 import BZ2File
        obj = BZ2File(patchFile)

    open(filePath, "w").write(obj.read())
    return filePath


def do_patch(sourceDir, patchFile, level, target = ''):
    """simple function to apply patches.."""
    cwd = os.getcwd()
    os.chdir(sourceDir)

    check_file(patchFile)
    level = int(level)
    cmd = "patch -p%d %s< %s" % (level, target, patchFile)
    p = os.popen(cmd)
    o = p.readlines()
    retval = p.close()
    if retval:
        raise UtilError("ERROR: patch (%s) failed: %s" % (patchFile,
                                                          strlist (o)))

    os.chdir(cwd)


def strip_directory(top, excludelist=[]):
    for root, dirs, files in os.walk(top):
        for fn in files:
            frpath = os.path.join(root, fn)

            # real path in .pisi package
            p = '/' + removepathprefix(top, frpath)
            strip = True
            for exclude in excludelist:
                if p.startswith(exclude):
                    strip = False
                    ctx.ui.debug("%s [%s]" %(p, "NoStrip"))

            if strip:
                if strip_file(frpath):
                    ctx.ui.debug("%s [%s]" %(p, "stripped"))
                

def strip_file(filepath):
    """strip a file"""
    p = os.popen("file %s" % filepath)
    o = p.read()

    def run_strip(f, flags=""):
        p = os.popen("strip %s %s" %(flags, f))
        ret = p.close()
        if ret:
            raise UtilError, "strip command failed!"

    if "current ar archive" in o:
        run_strip(filepath, "-g")
        return True

    elif "SB executable" in o:
        run_strip(filepath)
        return True

    elif "SB shared object" in o:
        run_strip(filepath, "--strip-unneeded")
        # FIXME: warn for TEXTREL
        return True

    return False

def partition_freespace(directory):
    """ returns free space of given directory's partition """
    st = os.statvfs(directory)
    return st[statvfs.F_BSIZE] * st[statvfs.F_BFREE]

def clean_locks(top = '.'):
    for root, dirs, files in os.walk(top):
        for fn in files:
            if fn.endswith('.lock'):
                path = os.path.join(root, fn)
                ctx.ui.info('Removing lock %s', path)
                os.unlink(path)

########################################
# Package/Repository Related Functions #
########################################

def package_name(name, version, release):
    return  name + '-' + version + '-' + release + ctx.const.package_prefix
