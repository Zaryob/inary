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

# ActionsAPI Modules
import inary.actionsapi
from inary.actionsapi.inarytools import dodir, domove, dosym, insinto
from inary.actionsapi.shelltools import *
import inary.actionsapi.get as get

# Standard Python Modules
import os
import shlex
import shutil

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


WorkDir = "{0}-{1}".format(get.srcNAME(), get.srcVERSION().split('_')[-1])


class CompileError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[TexLife]: " + value)


class InstallError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[TexLife]: " + value)


class RunTimeError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[TexLife]: " + value)


def compile(parameters=''):
    """compiling texlive packages"""

    # Move sources according to tplobj files
    if moveSources():
        raise CompileError(_('Moving source files failed.'))
    # Generate config files
    if generateConfigFiles():
        raise CompileError(_('Generate config files failed.'))
    # Build format files
    if buildFormatFiles():
        raise CompileError(_('Building format files failed.'))


def install(parameters=''):
    """Installing texlive packages"""

    # Create symlinks from format to engines
    if createSymlinksFormat2Engines():
        raise InstallError(
            _('Creating symlinks from format to engines failed.'))

    # Installing docs
    if installDocFiles():
        raise InstallError(_('Installing docs failed.'))

    # Installing texmf, texmf-dist, tlpkg, texmf-var
    if installTexmfFiles():
        raise InstallError(_('Installing texmf files failed.'))

    # Installing config files
    if installConfigFiles():
        raise InstallError(_('Installing config files failed.'))

    # Handle config files
    if handleConfigFiles():
        raise InstallError(_('Handle config files failed.'))


def createSymlinksFormat2Engines():
    """Create symlinks from format to engines"""
    for formatfile in ls("{}/texmf/fmtutil/format*.cnf".format(get.curDIR())):
        symfile = open(formatfile)
        for line in symfile.readlines():
            if not line.startswith("#"):
                symbin = line.split(None)
                if "cont-" in symbin[0] or "metafun" in symbin[0] or "mptopdf" in symbin[0]:
                    ctx.ui.info(
                        _('Symlink \"{}\" skipped (special case)').format(
                            symbin[0]))
                elif "mf" in symbin[0]:
                    ctx.ui.info(
                        _('Symlink \"{0[0]}\" -> \"{0[1]}\" skipped (texlive-core takes care of it.').format(symbin))
                else:
                    if symbin[0] == symbin[1]:
                        ctx.ui.info(
                            _('Symlink \"{0[0]}\" -> \"{0[1]}\" skipped.').format(symbin))
                    elif can_access_file("{0}/usr/bin/{1}".format(get.installDIR(), symbin[0])):
                        ctx.ui.info(
                            _('Symlink \"{}\" skipped (file exists.)').format(
                                symbin[0]))
                    else:
                        ctx.ui.info(
                            _('Making symlink from {0[0]} to {0[1]}').format(symbin))
                        dodir("/usr/bin")
                        sym(symbin[1],
                            "{0}/usr/bin/{1}".format(get.installDIR(),
                                                     symbin[0]))
        symfile.close()


def installDocFiles():
    """Installing docs"""
    if "documentation" in get.srcNAME():
        if os.path.isdir("{}/texmf-doc".format(get.curDIR())):
            copytree("texmf-doc",
                     "{}/usr/share/texmf-doc".format(get.installDIR()))
    else:
        for removedir in ["texmf", "texmf-dist"]:
            if os.path.isdir("{0}/{1}/doc/".format(get.curDIR(), removedir)):
                shutil.rmtree("{0}/{1}/doc".format(get.curDIR(), removedir))


def installTexmfFiles():
    """Installing texmf, texmf-dist, tlpkg, texmf-var"""
    for installdoc in ["texmf", "texmf-dist", "tlpkg", "texmf-var"]:
        if os.path.isdir("{0}/{1}".format(get.curDIR(), installdoc)):
            if not installdoc == "texmf-var":
                shutil.copytree(
                    installdoc, "{0}/usr/share/{1}".format(get.installDIR(), installdoc))
            else:
                copytree(installdoc,
                         "{}/var/lib/texmf".format(get.installDIR()))


def installConfigFiles():
    """Installing config files"""
    if can_access_file("{0}/{1}.cfg".format(get.curDIR(), get.srcNAME())):
        insinto("/etc/texmf/updmap.d",
                "{0}/{1}.cfg".format(get.curDIR(), get.srcNAME()))

    if can_access_file(
            "{0}/{1}.config.ps".format(get.curDIR(), get.srcNAME())):
        insinto("/etc/texmf/dvips.d",
                "{0}/{1}.config.ps".format(get.curDIR(), get.srcNAME()))

    if can_access_file("{0}/{1}.config".format(get.curDIR(), get.srcNAME())):
        insinto("/etc/texmf/dvipdfm/config",
                "{0}/{1}.config".format(get.curDIR(), get.srcNAME()))

    if can_access_file(
            "{0}/language/{1}.def.config".format(get.curDIR(), get.srcNAME())):
        insinto("/etc/texmf/language.def.d",
                "{0}/language.{1}.def".format(get.curDIR(), get.srcNAME()))

    if can_access_file(
            "{0}/language.{1}.dat".format(get.curDIR(), get.srcNAME())):
        insinto("/etc/texmf/language.dat.d",
                "{0}/language.{1}.dat".format(get.curDIR(), get.srcNAME()))


def handleConfigFiles():
    """Handling config files"""
    for root, dirs, files in os.walk(
            "{}/usr/share/texmf".format(get.installDIR())):
        if not ("config" in root or "doc" in root):
            for configFile in files:
                if configFile.endswith(("cfg", "cnf")):
                    dirname = root.split("/")[-1]
                    if not os.path.isdir(
                            "{0}/etc/texmf/{1}.d".format(get.installDIR(), dirname)):
                        ctx.ui.info(
                            _('Creating \"/etc/texmf/{}.d\"').format(dirname))
                        dodir("/etc/texmf/{}.d".format(dirname))
                    ctx.ui.info(_('Moving (and symlinking) \"/usr/share/texmf/{0}\" to \"/etc/texmf/{1}.d\"').format(configFile,
                                                                                                                     dirname))
                    domove("/usr/share/texmf/{0}/{1}".format(dirname,
                                                             configFile), "/etc/texmf/{}.d".format(dirname))
                    dosym("/etc/texmf/{0}.d/{1}".format(dirname, configFile),
                          "/usr/share/texmf/{0}/{1}".format(dirname, configFile))


def addFormat(parameters):
    """Add format files"""
    if not os.path.isdir("{}/texmf/fmtutil/".format(get.curDIR())):
        makedirs("{}/texmf/fmtutil/".format(get.curDIR()))
    if not os.path.isfile(
            "{0}/texmf/fmtutil/format.{1}.cnf".format(get.curDIR(), get.srcNAME())):
        cnf_file = open(
            "{0}/texmf/fmtutil/format.{1}.cnf".format(get.curDIR(), get.srcNAME()), "w")
        cnf_file.write(
            "# Generated for {} by actionsapi/texlivemodules.py\n".format(get.srcNAME()))
        cnf_file.close()

    # TODO: Use regex for code simplification
    # Removing white-space characters
    parameters = " ".join(parameters.split())
    # Split parameters until the value "option"
    parameters = shlex.split(parameters)
    para_dict = {}
    for option in parameters:
        pair = option.strip()  # Remove whitespaces before "options" value
        # The value "options" may have multiple "=", thus split just one time
        pair = pair.split("=", 1)
        if len(pair) == 2:  # The list may contain values that are not pair
            para_dict[pair[0]] = pair[1]
            if pair[0] == "patterns" and pair[1] == '':
                # Specified in the texlive-module.eclass
                para_dict["patterns"] = '-'
            elif not pair[0] == 'patterns':
                para_dict["patterns"] = '-'

    cnf_file = open(
        '{0}/texmf/fmtutil/format.{1}.cnf'.format(get.curDIR(), get.srcNAME()), 'a')
    cnf_file.write(
        '{0[name]}\t{0[engine]}\t{0[patterns]}\t{0[options]}\n'.format(para_dict))
    cnf_file.close()


def moveSources():
    reloc = "texmf-dist"

    for tlpobjfile in os.listdir("tlpkg/tlpobj/"):
        jobsfile = open("tlpkg/tlpobj/{}".format(tlpobjfile))
        for line in jobsfile.readlines():
            if "RELOC" in line:
                path = line.split("/", 1)[-1]
                path = path.strip()
                filename = path.split("/", -1)
                dirname = os.path.dirname(path)
                if not os.path.isdir("{0}/{1}".format(reloc, dirname)):
                    os.system("mkdir -p {0}/{1}".format(reloc, dirname))
                shutil.move("{}".format(path),
                            "{0}/{1}".format(reloc, dirname))


def buildFormatFiles():
    """Build format files"""
    if os.path.isdir("{}/texmf/fmtutil/".format(get.curDIR())):
        for formatfile in ls(
                "{}/texmf/fmtutil/format*.cnf".format(get.curDIR())):
            makedirs("{}/texmf-var/web2c/".format(get.curDIR()))
            ctx.ui.info(_('Building format file {}').format(formatfile))
            export("TEXMFHOME",
                   "{0}/texmf:/{0}texmf-dist:{0}/texmf-var".format(get.curDIR()))
            export("VARTEXFONTS", "fonts")
            system(
                "env -u TEXINPUTS fmtutil --cnffile {} --fmtdir texmf-var/web2c --all".format(formatfile))


def addLanguageDat(parameter):
    """Create language.*.dat files"""
    parameter = parameter.split()
    para_dict = {}
    for option in parameter:
        pair = option.split("=")
        if len(
                pair) == 2:  # That's just a caution, the pair should have two items, not more not less
            para_dict[pair[0]] = pair[1]

    language_dat = open(
        '{0}/language.{1}.dat'.format(get.curDIR(), get.srcNAME()), 'a')
    language_dat.write('{0[name]}\t{0[file]}\n"'.format(para_dict))
    language_dat.close()

    if "synonyms" in para_dict:
        language_dat = open(
            '{0}/language.{1}.dat'.format(get.curDIR(), get.srcNAME()), 'a')
        language_dat.write("={}\n".format(para_dict["synonyms"]))
        language_dat.close()


def addLanguageDef(parameter):
    """Create language.*.def files"""
    parameter = parameter.split()
    para_dict = {}
    for option in parameter:
        pair = option.split("=")
        if len(
                pair) == 2:  # That's just a caution, the pair should have two items, not more not less
            para_dict[pair[0]] = pair[1]

    if "lefthyphenmin" in para_dict and not para_dict["lefthyphenmin"]:
        para_dict["lefthyphenmin"] = "2"
    if "righthyphenmin" in para_dict and not para_dict["righthyphenmin"]:
        para_dict["righthyphenmin"] = "3"

    language_def = open(
        '{0}/language.{1}.def'.format(get.curDIR(), get.srcNAME()), 'a')
    language_def.write("\\addlanguage{%s}{%s}{}{%s}{%s}\n" % (
        para_dict["name"], para_dict["file"], para_dict["lefthyphenmin"], para_dict["righthyphenmin"]))
    language_def.close()

    if "synonyms" in para_dict:
        language_def = open(
            '{0}/language.{1}.def'.format(get.curDIR(), get.srcNAME()), 'a')
        language_def.write("\\addlanguage{%s}{%s}{}{%s}{%s}\n" % (
            para_dict["synonyms"], para_dict["file"], para_dict["lefthyphenmin"], para_dict["righthyphenmin"]))
        language_def.close()


def generateConfigFiles():
    """Generate config files"""
    for tlpobjfile in ls("{}/tlpkg/tlpobj/*".format(get.curDIR())):
        jobsfile = open(tlpobjfile)
        for line in jobsfile.readlines():
            splitline = line.split(" ", 2)
            if splitline[0] == "execute":
                command = splitline[1]
                parameter = splitline[2].strip()
                if command == "addMap":
                    echo("{0}/{1}.cfg".format(get.curDIR, get.srcNAME()),
                         "Map {}".format(parameter))
                    ctx.ui.info(
                        _('Map {0} is added to {1}/{2}.cfg').format(parameter, get.curDIR(), get.srcNAME()))
                elif command == "addMixedMap":
                    echo("{0}/{1}.cfg".format(get.curDIR(), get.srcNAME()),
                         "MixedMap {}".format(parameter))
                    ctx.ui.info(
                        _('MixedMap {0} is added to {1}/{2}.cfg').format(parameter, get.curDIR(), get.srcNAME()))
                elif command == "addDvipsMap":
                    echo("{0}/{1}-config.ps".format(get.curDIR(),
                                                    get.srcNAME()), "p +{}".format(parameter))
                    ctx.ui.info(
                        _('p +{0} is added to {1}/{2}-config.ps').format(parameter, get.curDIR(), get.srcNAME()))
                elif command == "addDvipdfmMap":
                    echo("{0}/{1}-config".format(get.curDIR(),
                                                 get.srcNAME()), "f {}".format(parameter))
                    ctx.ui.info(
                        _('f {0} is added to {1}/{2}-config').format(parameter, get.curDIR(), get.srcNAME()))
                elif command == "AddHyphen":
                    addLanguageDat(parameter)
                    addLanguageDef(parameter)
                elif command == "AddFormat":
                    addFormat(parameter)
                elif command == "BuildFormat":
                    ctx.ui.info(
                        _('Language file  {}  already generated.').format(parameter))
                elif command == "BuildLanguageDat":
                    ctx.ui.info(
                        _('No rule to proccess {}. Please file a bug.').format(command))
        jobsfile.close()
