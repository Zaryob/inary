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

"""INARY source/package index"""

# Standart Python Modules
import os
import re
import shutil
import multiprocessing

# Inary Modules
import inary.file
import inary.errors
import inary.package
import inary.util as util
import inary.context as ctx
import inary.operations.build
import inary.data.group as group
import inary.data.metadata as metadata
import inary.data.specfile as specfile
import inary.data.component as component

# AutoXML Library
import inary.sxml.autoxml as autoxml
import inary.sxml.xmlfile as xmlfile

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

# Inary Libraries


class Index(xmlfile.XmlFile, metaclass=autoxml.autoxml):
    tag = "INARY"

    t_Distribution = [component.Distribution, autoxml.optional]
    t_Specs = [[specfile.SpecFile], autoxml.optional, "SpecFile"]
    t_Packages = [[metadata.Package], autoxml.optional, "Package"]
    # t_Metadatas = [ [metadata.MetaData], autoxml.optional, "MetaData"]
    t_Components = [[component.Component], autoxml.optional, "Component"]
    t_Groups = [[group.Group], autoxml.optional, "Group"]

    def read_uri(self, uri, tmpdir, force=False):
        return self.read(uri, tmpDir=tmpdir, sha1sum=not force,
                         compress=inary.file.File.COMPRESSION_TYPE_AUTO,
                         sign=inary.file.File.detached,
                         copylocal=True, nodecode=True)

    # read index for a given repo, force means download even if remote not
    # updated
    def read_uri_of_repo(self, uri, repo=None, force=False):
        """Read PSPEC file"""
        if repo:
            tmpdir = os.path.join(ctx.config.index_dir(), repo)
        else:
            tmpdir = os.path.join(ctx.config.tmp_dir(), 'index')

        util.clean_dir(tmpdir)
        util.ensure_dirs(tmpdir)

        # write uri
        urlfile = open(util.join_path(tmpdir, 'uri'), 'w')
        urlfile.write(uri)  # uri
        urlfile.close()

        self.read_uri(uri, tmpdir, force)

        if not repo:
            repo = self.distribution.name()
            # and what do we do with it? move it to index dir properly
            newtmpdir = os.path.join(ctx.config.index_dir(), repo)
            util.clean_dir(newtmpdir)  # replace newtmpdir
            shutil.move(tmpdir, newtmpdir)

    @staticmethod
    def check_signature(filename, repo):
        tmpdir = os.path.join(ctx.config.index_dir(), repo)
        inary.file.File.check_signature(filename, tmpdir)

    def index(self, repo_uri, skip_sources=False):
        self.repo_dir = repo_uri

        packages = []
        specs = []
        deltas = {}

        ctx.ui.info(_("* Generating index tree...\n"), color="cyan")

        pkgs_sorted = False
        for fn in os.walk(repo_uri).__next__()[2]:
            if fn.endswith(ctx.const.delta_package_suffix) or fn.endswith(
                    ctx.const.package_suffix):
                pkgpath = os.path.join(repo_uri,
                                       util.parse_package_dir_path(fn))
                if not os.path.isdir(pkgpath):
                    os.makedirs(pkgpath)
                ctx.ui.info("{:80.80}\r".format(_(' -> Sorting:  \"{}\"').format(fn)),
                            noln=False if ctx.config.get_option("verbose") else True)
                shutil.copy2(os.path.join(repo_uri, fn), pkgpath)
                os.remove(os.path.join(repo_uri, fn))
                pkgs_sorted = True
        if pkgs_sorted:
            ctx.ui.info(
                "{:80.80}\r".format(
                    util.colorize(
                        _(' * Sorted:  \"{}\"').format(fn),
                        color="green")))

        for root, dirs, files in os.walk(repo_uri):
            # Filter hidden directories
            # TODO: Add --exclude-dirs parameter to CLI and filter according
            # directories here
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            for fn in files:

                if fn.endswith(ctx.const.delta_package_suffix):
                    name = util.parse_package_name_get_name(fn)
                    deltas.setdefault(name, []).append(os.path.join(root, fn))
                elif fn.endswith(ctx.const.package_suffix):
                    packages.append(os.path.join(root, fn))

                if fn == 'components.xml':
                    self.components.extend(
                        add_components(os.path.join(root, fn)))
                if fn == 'pspec.xml' and not skip_sources:
                    specs.append((os.path.join(root, fn), repo_uri))
                if fn == 'distribution.xml':
                    self.distribution = add_distro(os.path.join(root, fn))
                if fn == 'groups.xml':
                    self.groups.extend(add_groups(os.path.join(root, fn)))

        ctx.ui.info("")

        # Create a process pool, as many processes as the number of CPUs we
        # have
        try:
            obsoletes_list = list(map(str, self.distribution.obsoletes))
        except AttributeError:
            obsoletes_list = []
        if obsoletes_list:
            ctx.ui.info(
                _(" * Added obsoleted packages: [ {} ]".format(obsoletes_list)), color="blue", noln=False)

        pool = multiprocessing.Pool()

        # Before calling pool.map check if list is empty or not: python#12157
        if specs:
            ctx.ui.info(
                _(" * Adding source packages: "),
                color="blue",
                noln=False)
            try:
                # Add source packages to index using a process pool
                self.specs = pool.map(add_spec, specs)
                ctx.ui.info("\n")
            except BaseException:
                # If an exception occurs (like a keyboard interrupt),
                # immediately terminate worker processes and propagate
                # exception. (CLI honors KeyboardInterrupt exception, if you're
                # not using CLI, you must handle KeyboardException yourself)
                pool.terminate()
                pool.join()
                ctx.ui.info("")
                raise

        latest_packages = []

        for pkg in util.filter_latest_packages(packages):
            pkg_name = util.parse_package_name(os.path.basename(pkg))[0]
            if pkg_name.endswith(ctx.const.debug_name_suffix):
                pkg_name = util.remove_suffix(ctx.const.debug_name_suffix,
                                              pkg_name)
            if pkg_name not in obsoletes_list:
                # Currently, multiprocessing.Pool.map method accepts methods
                # with single parameters only. So we have to send our
                # parameters as a tuple to workaround that

                latest_packages.append((pkg, deltas, repo_uri))

        # Before calling pool.map check if list is empty or not: python#12157
        if latest_packages:
            sorted_pkgs = {}
            for pkg in latest_packages:
                key = re.search(r"\/((lib)?[\d\w])\/", pkg[0])
                key = key.group(1) if key else os.path.dirname(pkg[0])
                try:
                    sorted_pkgs[key].append(pkg)
                except KeyError:
                    sorted_pkgs[key] = [pkg]
            self.packages = []
            ctx.ui.info(
                _(" * Adding binary packages: "),
                color="blue",
                noln=False)
            for key, pkgs in sorted(sorted_pkgs.items()):
                ctx.ui.info("{:80.80}\r".format(
                    _("   -> Adding packages from directory \"{}\"... ".format(key))), noln=True)
                try:
                    # Add binary packages to index using a process pool
                    self.packages.extend(pool.map(add_package, pkgs))
                except BaseException:
                    pool.terminate()
                    pool.join()
                    ctx.ui.info("")
                    raise
                ctx.ui.info(
                    "{:80.80}\r".format(
                        _(
                            "   * Adding packages from directory \"{}\"... done.".format(key))),
                    color="green",
                    noln=False)
            ctx.ui.info(_("* Writing index file."), color="blue")

        pool.close()
        pool.join()


def add_package(params):
    try:
        path, deltas, repo_uri = params

        ctx.ui.info("{:80.80}\r".format(
            _('   -> Adding package to index: \"{}\"').format(os.path.basename(path))), noln=True)

        package = inary.package.Package(path)
        md = package.get_metadata()
        md.package.packageSize = int(os.path.getsize(path))
        md.package.packageHash = util.sha1_file(path)
        if ctx.config.options and ctx.config.options.absolute_urls:
            md.package.packageURI = os.path.realpath(path)
        else:
            md.package.packageURI = util.removepathprefix(repo_uri, path)

        # check package semantics
        errs = md.errors()
        if md.errors():
            ctx.ui.info("")
            ctx.ui.error(
                _(' * Package \"{}\": metadata corrupt, skipping...').format(md.package.name))
            ctx.ui.error(str(*errs))
        else:
            # No need to carry these with index (#3965)
            md.package.files = None
            md.package.additionalFiles = None

            if md.package.name in deltas:
                name, version, release, distro_id, arch = \
                    util.split_package_filename(path)

                for delta_path in deltas[md.package.name]:
                    src_release, dst_release, delta_distro_id, delta_arch = \
                        util.split_delta_package_filename(delta_path)[1:]

                    # Add only delta to latest build of the package
                    if dst_release != md.package.release or \
                            (delta_distro_id, delta_arch) != (distro_id, arch):
                        continue

                    delta = metadata.Delta()
                    delta.packageURI = util.removepathprefix(
                        repo_uri, delta_path)
                    delta.packageSize = int(os.path.getsize(delta_path))
                    delta.packageHash = util.sha1_file(delta_path)
                    delta.releaseFrom = src_release

                    md.package.deltaPackages.append(delta)

        return md.package

    except KeyboardInterrupt:
        # Handle KeyboardInterrupt exception to prevent ugly backtrace of all
        # worker processes and propagate the exception to main process.
        #
        # Probably it's better to use just 'raise' here, but multiprocessing
        # module has some bugs about that: (python#8296, python#9205 and
        # python#9207 )
        #
        # For now, worker processes do not propagate exceptions other than
        # Exception (like KeyboardInterrupt), so we have to manually propagate
        # KeyboardInterrupt exception as an Exception.

        raise Exception


def add_groups(path):
    ctx.ui.info(_(' * Adding \"groups.xml\" to index'))
    groups_xml = group.Groups()
    groups_xml.read(path)
    return groups_xml.groups


def add_components(path):
    ctx.ui.info(_(' * Adding \"components.xml\" to index'))
    components_xml = component.Components()
    components_xml.read(path)
    try:
        return components_xml.components
    except BaseException:
        ctx.ui.error(_(' * Component in {} is corrupt').format(path))


def add_distro(path):
    ctx.ui.info(_(' * Adding \"distribution.xml\" to index'))
    distro = component.Distribution()
    try:
        distro.read(path)
        return distro
    except BaseException:
        ctx.ui.error(_(' * Distribution in {} is corrupt').format(path))


def add_spec(params):
    try:
        path, repo_uri = params
        # TODO: may use try/except to handle this
        builder = inary.operations.build.Builder(path)
        builder.fetch_component()
        sf = builder.spec
        if ctx.config.options and ctx.config.options.absolute_urls:
            sf.source.sourceURI = os.path.realpath(path)
        else:
            sf.source.sourceURI = util.removepathprefix(repo_uri, path)

        ctx.ui.info("{:80.80}\r".format(_('   -> Adding source to index: \"{}\"').format(path)),
                    noln=False if ctx.config.get_option("verbose") else True)
        return sf

    except KeyboardInterrupt:
        # Multiprocessing hack, see add_package method for explanation
        raise Exception


# INDEXER
def index(dirs=None, output='inary-index.xml',
          skip_sources=False, skip_signing=False,
          compression=0):
    """Accumulate Inary XML files in a directory, and write an index."""
    index = Index()
    index.distribution = None
    if not dirs:
        dirs = ['.']
    for repo_dir in dirs:
        repo_dir = str(repo_dir)
        ctx.ui.info(
            _('Building index of Inary files under \"{}\" \n').format(repo_dir))
        index.index(repo_dir, skip_sources)

    sign = None if skip_signing else inary.file.File.detached
    index.write(output, sha1sum=True, compress=compression, sign=sign)
    ctx.ui.info(_('* Index file written.'), color="green")
