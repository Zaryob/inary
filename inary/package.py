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

"""package abstraction methods to add/remove files, extract control files"""

# Standard Python Modules
import os.path

# INARY Modules
import inary.ui
import inary.uri
import inary.file
import inary.errors
from . import fetcher
import inary.data.files
import inary.util as util
import inary.data.metadata
import inary.context as ctx
import inary.archive as archive

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class Error(inary.errors.Error):
    pass


class Package:
    """INARY Package Class provides access to a inary package (.inary
    file)."""

    formats = ("1.0", "1.1", "1.2", "1.3")
    default_format = "1.2"
    timestamp = None

    @staticmethod
    def archive_name_and_format(package_format):
        if package_format == "1.3":
            archive_format = "targz"
            archive_suffix = ctx.const.gz_suffix
        elif package_format == "1.2":
            archive_format = "tarxz"
            archive_suffix = ctx.const.xz_suffix
        elif package_format == "1.1":
            archive_format = "tarlzma"
            archive_suffix = ctx.const.lzma_suffix
        else:
            archive_format = "tar"
            archive_suffix = ""

        archive_name = ctx.const.install_tar + archive_suffix
        return archive_name, archive_format

    def __init__(self, packagefn, mode='r', format=None,
                 tmp_dir=None, pkgname='', no_fetch=False):
        self.filepath = packagefn
        self.destdir = ctx.config.dest_dir()
        url = inary.uri.URI(packagefn)

        if ("://" in self.filepath) and not no_fetch:
            self.fetch_remote_file(url)

        try:
            self.impl = archive.ArchiveZip(self.filepath, 'zip', mode)
        except IOError as e:
            raise Error(_("Cannot open package file: \"{}\"").format(e))

        self.install_archive = None

        if mode == "r":
            self.metadata = self.get_metadata()
            format = self.metadata.package.packageFormat

            # Many of the old packages do not contain format information
            # because of a bug in old Inary versions. This is a workaround
            # to guess their package format.
            if format is None:
                archive_name = ctx.const.install_tar + ctx.const.lzma_suffix
                if self.impl.has_file(archive_name):
                    format = "1.1"
                else:
                    format = "1.0"

        self.format = format or Package.default_format

        if self.format not in Package.formats:
            raise Error(_("Unsupported package format: {}").format(format))

        self.tmp_dir = tmp_dir or ctx.config.tmp_dir()

    def fetch_remote_file(self, url, pkgname=''):
        dest = ctx.config.cached_packages_dir()
        self.filepath = os.path.join(dest, url.filename())
        if not os.path.exists(self.filepath):
            try:
                inary.file.File.download(url, dest, pkgname)
            except fetcher.FetchError:
                # Bug 3465
                if ctx.get_option('reinstall'):
                    raise Error(_(
                        "There was a problem while fetching \"{}\".\nThe package may have been upgraded. Please try to upgrade the package.").format(
                        url))
                raise
        else:
            if ctx.config.get_option('debug'):
                ctx.ui.info(_('{} [cached]').format(url.filename()))

    def add_to_package(self, fn, an=None):
        """Add a file or directory to package"""
        self.impl.add_to_archive(fn, an)

    def add_to_install(self, name, arcname=None):
        """Add the file 'name' to the install archive"""

        if arcname is None:
            arcname = name

        if self.install_archive is None:
            archive_name, archive_format = \
                self.archive_name_and_format(self.format)
            self.install_archive_path = util.join_path(self.tmp_dir,
                                                       archive_name)
            ctx.build_leftover = self.install_archive_path
            self.install_archive = archive.ArchiveTar(
                self.install_archive_path,
                archive_format)

        self.install_archive.add_to_archive(name, arcname)

    def add_metadata_xml(self, path):
        self.metadata = inary.data.metadata.MetaData()
        self.metadata.read(path)

        self.add_to_package(path, ctx.const.metadata_xml)

    def add_files_xml(self, path):
        self.files = inary.data.files.Files()
        self.files.read(path)

        self.add_to_package(path, ctx.const.files_xml)

    def close(self):
        """Close the package archive"""
        if self.install_archive:
            self.install_archive.close()
            arcpath = self.install_archive_path
            arcname = os.path.basename(arcpath)
            if self.timestamp is not None:
                tstamp = self.timestamp
                os.utime(arcpath, (tstamp, tstamp))
            self.add_to_package(arcpath, arcname)

        self.impl.close()

        if self.install_archive:
            os.unlink(self.install_archive_path)
            ctx.build_leftover = None

    def get_install_archive(self):
        archive_name, archive_format = \
            self.archive_name_and_format(self.format)

        if archive_name is None or not self.impl.has_file(archive_name):
            return

        archive_file = self.impl.open(archive_name)
        tar = archive.ArchiveTar(fileobj=archive_file,
                                 arch_type=archive_format,
                                 no_same_permissions=False,
                                 no_same_owner=False)

        return tar

    def extract(self, outdir):
        """Extract entire package contents to directory"""
        self.extract_dir('', outdir)  # means package root

    def extract_files(self, paths, outdir):
        """Extract paths to outdir"""
        self.impl.unpack_files(paths, outdir)

    def extract_file(self, path, outdir):
        """Extract file with path to outdir"""
        self.extract_files([path], outdir)

    def extract_file_synced(self, path, outdir):
        """Extract file with path to outdir"""
        data = self.impl.read_file(path)
        fpath = util.join_path(outdir, path)
        util.ensure_dirs(os.path.dirname(fpath))

        with open(fpath, "wb") as f:
            f.write(data.encode("utf-8"))
            f.flush()
            os.fsync(f.fileno())

    def extract_dir(self, dir, outdir):
        """Extract directory recursively, this function
        copies the directory archiveroot/dir to outdir"""
        self.impl.unpack_dir(dir, outdir)

    def extract_install(self, outdir):
        def callback(tarinfo, extracted):
            if not extracted:
                # Installing packages (especially shared libraries) is a
                # bit tricky. You should also change the inode if you
                # change the file, cause the file is opened allready and
                # accessed. Removing and creating the file will also
                # change the inode and will do the trick (in fact, old
                # file will be deleted only when its closed).
                #
                # Also, tar.extract() doesn't write on symlinks...
                # We remove file symlinks before (directory symlinks
                # broke system)
                if not os.path.isdir(self.destdir+"/"+tarinfo.name):
                    if os.path.islink(self.destdir+"/"+tarinfo.name):
                        link = os.readlink(self.destdir+"/"+tarinfo.name)
                        if not os.path.isdir(self.destdir+"/"+link):
                            try:
                                if os.path.exists(self.destdir+"/"+tarinfo.name):
                                    os.unlink(self.destdir+"/"+tarinfo.name)
                            except OSError as e:
                                ctx.ui.warning(e)
                    else:
                        try:
                            if os.path.exists(self.destdir+"/"+tarinfo.name):
                                os.unlink(self.destdir+"/"+tarinfo.name)
                        except OSError as e:
                            ctx.ui.warning(e)

            else:
                # Added for package-manager
                if tarinfo.name.endswith(".desktop"):
                    ctx.ui.notify(
                        inary.ui.desktopfile,
                        logging=False,
                        desktopfile=tarinfo.name)

        tar = self.get_install_archive()

        if tar:
            tar.unpack_dir(outdir, callback=callback)
        else:
            self.extract_dir_flat('install', outdir)

    def extract_dir_flat(self, dir, outdir):
        """Extract directory recursively, this function
        unpacks the *contents* of directory archiveroot/dir inside outdir
        this is the function used by the installer"""
        self.impl.unpack_dir_flat(dir, outdir)

    def extract_to(self, outdir, clean_dir=False):
        """Extracts contents of the archive to outdir. Before extracting if clean_dir
        is set, outdir is deleted with its contents"""
        self.impl.unpack(outdir, clean_dir)

    def extract_inary_files(self, outdir):
        """Extract INARY control files: metadata.xml, files.xml,
        action scripts, etc."""
        self.extract_files(
            [ctx.const.metadata_xml, ctx.const.files_xml], outdir)
        self.extract_dir('config', outdir)

    def get_metadata(self):
        """reads metadata.xml from the INARY package and returns MetaData object"""
        md = inary.data.metadata.MetaData()
        md.parse(self.impl.read_file(ctx.const.metadata_xml))
        return md

    def get_files(self):
        """reads files.xml from the INARY package and returns Files object"""
        files = inary.data.files.Files()
        files.parse(self.impl.read_file(ctx.const.files_xml))
        return files

    def read(self):
        self.files = self.get_files()
        self.metadata = self.get_metadata()

    def pkg_dir(self):
        packageDir = self.metadata.package.name + '-' \
            + self.metadata.package.version + '-' \
            + self.metadata.package.release

        return os.path.join(ctx.config.packages_dir(), packageDir)

    @staticmethod
    def is_cached(packagefn):
        url = inary.uri.URI(packagefn)
        filepath = packagefn
        if url.is_remote_file():
            filepath = os.path.join(
                ctx.config.cached_packages_dir(),
                url.filename())
            return os.path.exists(filepath) and filepath
        else:
            return filepath
