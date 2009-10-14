# -*- coding: utf-8 -*-
#
# Copyright (C) 2009, TUBITAK/UEKAE
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

    # Build format files
    if buildFormatFiles():
        raise CompileError, _('Building format files failed')
    # Generate config files
    if generateConfigFiles():
        raise CompileError, _('Generate config files failed')

def install(parameters = ''):
    '''Installing texlive packages'''

    # Create symlinks from format to engines
    if createSymlinksFormat2Engines():
        raise InstallError, _('Creating symlinks from format to engines failed')

    # Installing texmf, texmf-dist, tlpkg, texmf-var
    if installTexmfFiles():
        raise InstallError, _('Installing texmf files failed')

    # Installing docs
    if installDocFiles():
        raise InstallError, _('Installing docs failed')

    # Installing config files
    if installConfigFiles():
        raise InstallError, _('Installing config files failed')

    # Handle config files
    if os.path.isdir("%s/texmf" % get.curDIR()):
        cd("%s/usr/share/texmf" % get.installDIR())
        if handleConfigFiles(".", "cfg", "cnf"):
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

def installTexmfFiles():
    '''Installing texmf, texmf-dist, tlpkg, texmf-var'''
    for installdoc in ["texmf", "texmf-dist", "tlpkg", "texmf-var"]:
        if os.path.isdir("%s/%s" % (get.curDIR(), installdoc)):
            if not installdoc == "texmf-var":
                copytree(installdoc, "%s/usr/share/%s" % (get.installDIR(), installdoc))
            else:
                copytree(installdoc, "%s/var/lib/texmf" % get.installDIR())


def installDocFiles():
    '''Installing docs'''
    if not "documentation" in get.srcNAME():
        if os.path.isdir("%s/texmf-doc" % get.curDIR()):
            copytree("texmf-doc", "%s/usr/share/texmf-doc" % get.installDIR())
    else:
        for removedir in ["texmf", "texmf-dist"]:
            if os.path.isdir("%s/%s/doc/" % (get.curDIR(), removedir)):
                removeDir("/usr/share/%s/doc" % removedir )


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

def handleConfigFiles(currdir,ext1, ext2):
    '''Handling config files'''
    for conffile in ls(currdir):
        configpath = os.path.join(currdir, conffile)
        if os.path.isfile(configpath):
             if configpath.endswith(ext1) or configpath.endswith(ext2):
                if not "config" in configpath:
                    handledir=currdir.split('/')
                    if not os.path.isdir("%s/etc/texmf/%s.d" % (get.installDIR(),handledir[1])):
                        ctx.ui.info(_('Creating /etc/texmf/%s.d') % handledir[1])
                        dodir("/etc/texmf/%s.d" % handledir[1])
                    domove("/usr/share/texmf/%s/%s" % (handledir[1], conffile), "/etc/texmf/%s.d" % handledir[1])
                    dosym("/etc/texmf/%s.d/%s" % (handledir[1], conffile), "/usr/share/texmf/%s/%s" % (handledir[1], conffile))

        else:
           handleConfigFiles(configpath,ext1, ext2)

def buildFormatFiles():
    '''Build format files'''
    if os.path.isdir("%s/texmf/fmtutil/" % get.curDIR()):
        makedirs("texmf-var/web2c")
        for formatfile in ls("%s/texmf/fmtutil/format*.cnf" % get.curDIR()):
            ctx.ui.info(_('Building format file %s') % formatfile)
            export("TEXMFHOME", "texmf:texmf-dist")
            system("fmtutil --cnffile %s --fmtdir texmf-var/web2c --all" % formatfile)

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
                    makeLanguagesDefDatLines(parameter)
                elif command == "BuildFormat":
                    ctx.ui.info(_('Language file  %s  already generated.') % parameter)
                elif command == "BuildLanguageDat":
                    ctx.ui.info(_('No rule to proccess %s. Please file a bug.') % command)
        jobsfile.close()

def makeLanguagesDefDatLines(parameter):
    '''Make Languages Def Dat Lines'''
    splitspace=parameter.split(None)
    if len(splitspace) == 4:
        name = splitspace[0].split("=")

        lefthyphenmin = splitspace[1].split("=")
        if not lefthyphenmin[1]:
            lefthyphenmin[1]= "2"

        righthyphenmin = splitspace[2].split("=")
        if not righthyphenmin[1]:
            righthyphenmin[1]= "3"

        datdeffile = splitspace[3].split("=")
    else:
        name = splitspace[0].split("=")
        synonyms = splitspace[1].split("=")

        lefthyphenmin = splitspace[2].split("=")
        if not lefthyphenmin[1]:
             lefthyphenmin[1]= "2"

        righthyphenmin = splitspace[3].split("=")
        if not righthyphenmin[1]:
            righthyphenmin[1]= "3"

        datdeffile = splitspace[4].split("=")

        synonym = synonyms[1].split(",")
        for i in range(len(synonym)):
            echo("%s/language.%s.def" % (get.curDIR(), get.srcNAME()), "\\languages{%s}{%s}{}{%s}{%s}" % (synonym[i], datdeffile[1], lefthyphenmin[1], righthyphenmin[1]))
            ctx.ui.info(_('\\languages{%s}{%s}{}{%s}{%s} is added to %s/language.%s.def') % (synonym[i], datdeffile[1], lefthyphenmin[1], righthyphenmin[1], get.curDIR(), get.srcNAME()))

            echo("%s/language.%s.dat" % (get.curDIR(), get.srcNAME()), "=%s"  % (synonym[i]))
            ctx.ui.info(_('%s is added to %s/language.%s.dat') % (synonym[i], get.curDIR(), get.srcNAME()))

    echo("%s/language.%s.def" % (get.curDIR(), get.srcNAME()), "\\languages{%s}{%s}{}{%s}{%s}" % (name[1], datdeffile[1], lefthyphenmin[1], righthyphenmin[1]))
    ctx.ui.info(_('\\languages{%s}{%s}{}{%s}{%s} is added to %s/language.%s.def ') % (name[1], datdeffile[1], lefthyphenmin[1], righthyphenmin[1], get.curDIR(), get.srcNAME()))

    echo("%s/language.%s.dat" % (get.curDIR(), get.srcNAME()), "%s %s"  % (name[1], datdeffile[1]))
    ctx.ui.info(_('%s %s is added to %s/language.%s.dat ') % (name[1], datdeffile[1], get.curDIR(), get.srcNAME()))
