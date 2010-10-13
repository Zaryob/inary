# -*- coding: utf-8 -*-
#
# Copyright (C) 2009-2010 TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

# standard python modules
import os
import glob
import shutil
import shlex
import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

# Pisi Modules
import pisi.context as ctx

# ActionsAPI Modules
import pisi.actionsapi
import pisi.actionsapi.get as get
from pisi.actionsapi.shelltools import *
from pisi.actionsapi.pisitools import dodoc, dodir, domove, dosym, insinto, removeDir


WorkDir = "%s-%s" % (get.srcNAME(), get.srcVERSION().split('_')[-1])

class CompileError(pisi.actionsapi.Error):
    def __init__(self, value=''):
        pisi.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)

class InstallError(pisi.actionsapi.Error):
    def __init__(self, value=''):
        pisi.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)

class RunTimeError(pisi.actionsapi.Error):
    def __init__(self, value=''):
        pisi.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)

def compile(parameters = ''):
    '''compiling texlive packages'''

    # Move sources according to tplobj files
    if moveSources():
        raise CompileError, _('Moving source files failed')
    # Generate config files
    if generateConfigFiles():
        raise CompileError, _('Generate config files failed')
    # Build format files
    if buildFormatFiles():
        raise CompileError, _('Building format files failed')

def install(parameters = ''):
    '''Installing texlive packages'''

    # Create symlinks from format to engines
    if createSymlinksFormat2Engines():
        raise InstallError, _('Creating symlinks from format to engines failed')

    # Installing docs
    if installDocFiles():
        raise InstallError, _('Installing docs failed')

    # Installing texmf, texmf-dist, tlpkg, texmf-var
    if installTexmfFiles():
        raise InstallError, _('Installing texmf files failed')

    # Installing config files
    if installConfigFiles():
        raise InstallError, _('Installing config files failed')

    # Handle config files
    if handleConfigFiles():
        raise Installing, _('Handle config files failed')

def createSymlinksFormat2Engines():
    '''Create symlinks from format to engines'''
    for formatfile in ls("%s/texmf/fmtutil/format*.cnf" % get.curDIR()):
        symfile = open(formatfile, "r")
        for line in symfile.readlines():
            if not line.startswith("#"):
                symbin = line.split(None)
                if "cont-" in symbin[0] or "metafun" in symbin[0] or "mptopdf" in symbin[0]:
                     ctx.ui.info(_('Symlink %s skipped (special case)') % symbin[0])
                elif "mf" in symbin[0]:
                    ctx.ui.info(_('Symlink %s -> %s skipped (texlive-core takes care of it.') % (symbin[0], symbin[1]))
                else:
                    if symbin[0] == symbin[1]:
                        ctx.ui.info(_('Symlink %s -> %s skipped.') % (symbin[0], symbin[1]))
                    elif can_access_file("%s/usr/bin/%s" % (get.installDIR(), symbin[0])):
                        ctx.ui.info(_('Symlink %s skipped (file exists.)') % symbin[0])
                    else:
                        ctx.ui.info(_('Making symlink from %s to %s') % (symbin[0], symbin[1]))
                        dodir("/usr/bin")
                        sym(symbin[1], "%s/usr/bin/%s" % (get.installDIR(), symbin[0]))
        symfile.close()

def installDocFiles():
    '''Installing docs'''
    if "documentation" in get.srcNAME():
        if os.path.isdir("%s/texmf-doc" % get.curDIR()):
            copytree("texmf-doc", "%s/usr/share/texmf-doc" % get.installDIR())
    else:
        for removedir in ["texmf", "texmf-dist"]:
            if os.path.isdir("%s/%s/doc/" % (get.curDIR(), removedir)):
                shutil.rmtree("%s/%s/doc" % (get.curDIR(),removedir))

def installTexmfFiles():
    '''Installing texmf, texmf-dist, tlpkg, texmf-var'''
    for installdoc in ["texmf", "texmf-dist", "tlpkg", "texmf-var"]:
        if os.path.isdir("%s/%s" % (get.curDIR(), installdoc)):
            if not installdoc == "texmf-var":
                shutil.copytree(installdoc, "%s/usr/share/%s" % (get.installDIR(),installdoc))
            else:
                copytree(installdoc, "%s/var/lib/texmf" % get.installDIR())

def installConfigFiles():
    '''Installing config files'''
    if can_access_file("%s/%s.cfg" % (get.curDIR(), get.srcNAME())):
        insinto("/etc/texmf/updmap.d", "%s/%s.cfg" % ( get.curDIR(), get.srcNAME()))

    if can_access_file("%s/%s-config.ps" % (get.curDIR(), get.srcNAME())):
        insinto("/etc/texmf/dvips.d", "%s/%s-config.ps" % (get.curDIR(), get.srcNAME()))

    if can_access_file("%s/%s-config" % (get.curDIR(), get.srcNAME())):
        insinto("/etc/texmf/dvipdfm/config", "%s/%s-config" % (get.curDIR(), get.srcNAME()))

    if can_access_file("%s/language.%s.def" % (get.curDIR(), get.srcNAME())):
        insinto("/etc/texmf/language.def.d", "%s/language.%s.def" % (get.curDIR(), get.srcNAME()))

    if can_access_file("%s/language.%s.dat" % (get.curDIR(), get.srcNAME())):
        insinto( "/etc/texmf/language.dat.d", "%s/language.%s.dat" % (get.curDIR(), get.srcNAME()))

def handleConfigFiles():
    '''Handling config files'''
    for root, dirs,files in os.walk("%s/usr/share/texmf" % get.installDIR()):
        if not ("config" in root or "doc" in root):
            for configFile in files:
                if configFile.endswith(("cfg", "cnf")):
                    dirname = root.split("/")[-1]
                    if not os.path.isdir("%s/etc/texmf/%s.d" % (get.installDIR(),dirname)):
                        ctx.ui.info(_('Creating /etc/texmf/%s.d') % dirname)
                        dodir("/etc/texmf/%s.d" % dirname)
                    ctx.ui.info(_('Moving (and symlinking) /usr/share/texmf/%s to /etc/texmf/%s.d') % (configFile,dirname))
                    domove("/usr/share/texmf/%s/%s" % (dirname,configFile), "/etc/texmf/%s.d" % dirname)
                    dosym("/etc/texmf/%s.d/%s" % (dirname, configFile), "/usr/share/texmf/%s/%s" %(dirname, configFile))

def addFormat(parameters):
    '''Add format files'''
    if not os.path.isdir("%s/texmf/fmtutil/" % get.curDIR()):
        makedirs("%s/texmf/fmtutil/" % get.curDIR())
    if not os.path.isfile("%s/texmf/fmtutil/format.%s.cnf" % (get.curDIR(),get.srcNAME())):
        cnf_file = open("%s/texmf/fmtutil/format.%s.cnf" % (get.curDIR(),get.srcNAME()), "w")
        cnf_file.write("# Generated for %s by actionsapi/texlivemodules.py\n" % get.srcNAME())
        cnf_file.close()

    # TODO: Use regex for code simplification
    parameters = " ".join(parameters.split())   # Removing white-space characters
    parameters = shlex.split(parameters)      # Split parameters until the value "option"
    para_dict = {}
    for option in parameters:
        pair = option.strip()                   # Remove whitespaces before "options" value
        pair = pair.split("=",1)                # The value "options" may have multiple "=", thus split just one time
        if len(pair) == 2:                      # The list may contain values that are not pair
            para_dict[pair[0]] = pair[1]
            if pair[0] == "patterns" and pair[1] == '':
                para_dict["patterns"] = '-'     # Specified in the texlive-module.eclass
            elif not pair[0] == 'patterns':
                para_dict["patterns"] = '-'

    cnf_file = open('%s/texmf/fmtutil/format.%s.cnf' % (get.curDIR(),get.srcNAME()), 'a')
    cnf_file.write("%s\t%s\t%s\t%s\n" % (para_dict["name"], para_dict["engine"], para_dict["patterns"], para_dict["options"]))
    cnf_file.close()

def moveSources():
    reloc = "texmf-dist"

    for tlpobjfile in os.listdir("tlpkg/tlpobj/"):
        jobsfile=open("tlpkg/tlpobj/%s" % tlpobjfile, "r")
        for line in jobsfile.readlines():
            if "RELOC" in line:
                path = line.split("/", 1)[-1]
                path = path.strip()
                filename = path.split("/", -1)
                dirname = os.path.dirname(path)
                if not os.path.isdir("%s/%s" % (reloc,dirname)):
                    os.system("mkdir -p %s/%s" % (reloc,dirname))
                shutil.move("%s" % path , "%s/%s" % (reloc,dirname))

def buildFormatFiles():
    '''Build format files'''
    if os.path.isdir("%s/texmf/fmtutil/" % get.curDIR()):
        for formatfile in ls("%s/texmf/fmtutil/format*.cnf" % get.curDIR()):
            makedirs("%s/texmf-var/web2c/" % get.curDIR())
            ctx.ui.info(_('Building format file %s') % formatfile)
            export("TEXMFHOME", "%s/texmf:/%stexmf-dist:%s/texmf-var" %(get.curDIR(), get.curDIR(), get.curDIR() ))
            export("VARTEXFONTS", "fonts")
            system("env -u TEXINPUTS fmtutil --cnffile %s --fmtdir texmf-var/web2c --all" % formatfile)

def addLanguageDat(parameter):
    '''Create language.*.dat files'''
    parameter = parameter.split()
    para_dict={}
    for option in parameter:
        pair = option.split("=")
        if len(pair) == 2: #That's just a caution, the pair should have two items, not more not less
            para_dict[pair[0]] = pair[1]

    language_dat = open('%s/language.%s.dat' % (get.curDIR(),get.srcNAME())  , 'a')
    language_dat.write("%s\t%s\n" % (para_dict["name"], para_dict["file"]))
    language_dat.close()

    if "synonyms" in para_dict:
        language_dat = open('%s/language.%s.dat' % (get.curDIR(),get.srcNAME())  , 'a')
        language_dat.write("=%s\n" % para_dict["synonyms"])
        language_dat.close()

def addLanguageDef(parameter):
    '''Create language.*.def files'''
    parameter = parameter.split()
    para_dict={}
    for option in parameter:
        pair = option.split("=")
        if len(pair) == 2: #That's just a caution, the pair should have two items, not more not less
            para_dict[pair[0]] = pair[1]

    if "lefthyphenmin" in para_dict and not para_dict["lefthyphenmin"]:
        para_dict["lefthyphenmin"] = "2"
    if "righthyphenmin" in para_dict and not para_dict["righthyphenmin"]:
        para_dict["righthyphenmin"] = "3"

    language_def = open('%s/language.%s.def' % (get.curDIR(),get.srcNAME())  , 'a')
    language_def.write("\\addlanguage{%s}{%s}{}{%s}{%s}\n" % (para_dict["name"], para_dict["file"],  para_dict["lefthyphenmin"],  para_dict["righthyphenmin"]))
    language_def.close()

    if "synonyms" in para_dict:
        language_def = open('%s/language.%s.def' % (get.curDIR(),get.srcNAME())  , 'a')
        language_def.write("\\addlanguage{%s}{%s}{}{%s}{%s}\n" % (para_dict["synonyms"], para_dict["file"],  para_dict["lefthyphenmin"],  para_dict["righthyphenmin"]))
        language_def.close()

def generateConfigFiles():
    '''Generate config files'''
    for tlpobjfile in ls("%s/tlpkg/tlpobj/*" % get.curDIR()):
        jobsfile=open(tlpobjfile, "r")
        for line in jobsfile.readlines():
            splitline = line.split(" ", 2)
            if splitline[0] == "execute":
                command = splitline[1]
                parameter = splitline[2].strip()
                if command == "addMap":
                    echo("%s/%s.cfg" % (get.curDIR(), get.srcNAME()), "Map %s" % parameter)
                    ctx.ui.info(_('Map %s is added to %s/%s.cfg') % (parameter, get.curDIR(), get.srcNAME()))
                elif command == "addMixedMap":
                    echo("%s/%s.cfg" % (get.curDIR(), get.srcNAME()), "MixedMap %s" % parameter)
                    ctx.ui.info(_('MixedMap %s is added to %s/%s.cfg') % (parameter, get.curDIR(), get.srcNAME()))
                elif command == "addDvipsMap":
                    echo("%s/%s-config.ps" % (get.curDIR(), get.srcNAME()), "p +%s" % parameter)
                    ctx.ui.info(_('p +%s is added to %s/%s-config.ps') % (parameter, get.curDIR(), get.srcNAME()))
                elif command == "addDvipdfmMap":
                    echo("%s/%s-config" % (get.curDIR(), get.srcNAME()), "f %s" % parameter)
                    ctx.ui.info(_('f %s is added to %s/%s-config') % (parameter, get.curDIR(), get.srcNAME()))
                elif command == "AddHyphen":
                    addLanguageDat(parameter)
                    addLanguageDef(parameter)
                elif command == "AddFormat":
                    addFormat(parameter)
                elif command == "BuildFormat":
                    ctx.ui.info(_('Language file  %s  already generated.') % parameter)
                elif command == "BuildLanguageDat":
                    ctx.ui.info(_('No rule to proccess %s. Please file a bug.') % command)
        jobsfile.close()

