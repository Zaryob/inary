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

# Standard Python Modules
import os
from glob import glob

# Inary Modules
import inary.context as ctx

# ActionsAPI Modules
import inary.actionsapi
import inary.actionsapi.get as get
from inary.actionsapi.shelltools import system
from inary.actionsapi.shelltools import isEmpty
from inary.actionsapi.shelltools import export

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class ConfigureError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[RubyModules]: " + value)


class CompileError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[RubyModules]: " + value)


class InstallError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[RubyModules]: " + value)


class RunTimeError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[RubyModules]: " + value)


def get_config(config):
    return os.popen(
        "ruby -rrbconfig -e 'puts RbConfig::CONFIG[\"{}\"]'".format(config)).read().strip()


def get_ruby_version():
    return get_config('ruby_version')


def get_rubylibdir():
    return get_config('rubylibdir')


def get_sitedir():
    return get_config('sitedir')


def get_gemdir():
    return os.popen('gem env gemdir').read().strip()


def get_ruby_install_name():
    return get_config('ruby_install_name')


def get_gemhome():
    (rubylibdir, ruby_version) = os.path.split(get_rubylibdir())

    return os.path.join(get.installDIR(), rubylibdir.lstrip(
        '/'), 'gems', ruby_version)


def get_sitelibdir():
    return get_config('sitelibdir')


def generate_gemname():
    return "-".join(get.srcNAME().split("-")[1:])


def auto_dodoc():
    from inary.actionsapi.inarytools import dodoc

    docs = ('AUTHORS', 'CHANGELOG', 'CONTRIBUTORS', 'Change*', 'KNOWN_BUGS',
            'MAINTAINERS', 'NEWS', 'README*', 'History.txt')

    for doc_glob in docs:
        for doc in glob(doc_glob):
            if not isEmpty(doc):
                dodoc(doc)


def install(parameters=''):
    """does ruby setup.rb install"""
    if system(
            'ruby -w setup.rb --prefix=/{0}/{1} --destdir={1} {2}'.format(get.defaultprefixDIR(), get_gemdir(), get.installDIR(), parameters)):
        raise InstallError(_('Install failed.'))

    auto_dodoc()


def rake_install(parameters=''):
    """execute rake script for installation"""
    if system('rake -t -l {0} {1}'.format(os.path.join('/',
                                                       get.defaultprefixDIR(), 'lib'), parameters)):
        raise InstallError(_('Install failed.'))

    auto_dodoc()


def gem_build(parameters=''):
    if system('gem build {} {}'.format(generate_gemname(), parameters)):
        raise InstallError(_('Build failed.'))


def gem_install(parameters=''):
    """Make installation from GemFile"""
    if system('gem install --backtrace {0} -i "{1}{2}"  -n "{1}/usr/bin" {3}.gem'.format(
            parameters, get.installDIR(), get_gemdir(), generate_gemname() + "-" + get.srcVERSION())):
        raise InstallError(_('Install failed.'))

    auto_dodoc()


def run(parameters=''):
    """executes parameters with ruby"""
    export('DESTDIR', get.installDIR())

    if system('ruby {}'.format(parameters)):
        raise RuntimeError(_("Running 'ruby {}' failed.").format(parameters))
