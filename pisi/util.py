# -*- coding: utf-8 -*-
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
from ui import ui

class FileError(Exception):
    pass

class UtilError(Exception):
    pass


#########################
# string/list functions #
#########################

def unzip(seq):
    return zip(*seq)

def concat(l):
    """concatenate a list of lists"""
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
    "check if all elements of a sequence are equal"
    if len(l)==0:
        return True
    else:
        last = l.pop()
        for x in l:
            if x!=last:
                return False
        return True

def prefix(a, b):
    "check if sequence a is a prefix of sequence b"
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


#############################
# Path Processing Functions #
#############################

def splitpath(a):
    """split path into components and return as a list
    os.path.split doesn't do what I want"""
    l = a.split(os.path.sep)
    if l[len(l)-1]=='':
        l.pop()
    return l

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

def clean_dir(top):
    "Remove all content of a directory (top)"
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

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

def get_file_hashes(top, excludePrefixes=None, removePrefix=None):
    """Generator function iterates over a toplevel path and returns the
    (filePath, sha1Hash) tuple for all files. If excludePrefixes list
    is given as a parameter, function will exclude the filePaths
    matching those prefixes. The removePrefix string parameter will be
    used to remove prefix from filePath while matching excludes, if
    given."""
    for root, dirs, files in os.walk(top, topdown=False):
        # check if root matches an exclude, and continue
        if excludePrefixes and removePrefix:
            p = remove_prefix(removePrefix, root)
            if [e for e in excludePrefixes if p.startswith(e)]:
                continue

        for file in files:
            f = os.path.join(root, file)
            yield (f, sha1_file(f))

def copy_dir(src, dest):
    """copy source dir to destination dir recursively"""
    raise UtilError("not implemented")

def sha1_file(filename):
    """calculate sha1 hash of filename"""
    # Broken links can cause problem!
    try:
        m = sha.new()
        f = file(filename, 'rb')
        for l in f:
            m.update(l)
        return m.hexdigest()
    except IOError:
        return "0"     

def uncompress(patchFile, compressType="gz", targetDir=None):
    """uncompresses a file and returns the path of the uncompressed
    file"""
    if targetDir:
        filePath = os.path.join(targetDir,
                                os.path.basename(patchFile))
    else:
        filePath = os.path.basename(patchFile)

    fileObj = open(filePath, "w")

    if compressType == "gz":
        from gzip import GzipFile
        obj = GzipFile(patchFile)

    fileObj.write(obj.read())
    fileObj.close()
    return filePath


def do_patch(sourceDir, patchFile, p=0):
    """simple function to apply patches.."""
    cwd = os.getcwd()
    os.chdir(sourceDir)

    check_file(patchFile)
    cmd = "patch -p%d < %s" % (p, patchFile)
    p = os.popen(cmd)
    o = p.readlines()
    retval = p.close()
    if retval:
        raise UtilError("ERROR: patch (%s) failed: %s" % (patchFile,
                                                          strlist (o)))

    os.chdir(cwd)

def partition_freespace(directory):
    """ returns free space of given directory's partition """
    st = os.statvfs(directory)
    return st[statvfs.F_BSIZE] * st[statvfs.F_BFREE]
