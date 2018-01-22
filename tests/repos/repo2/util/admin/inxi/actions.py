#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/copyleft/gpl.txt

from inary.actionsapi import inarytools

WorkDir = "."

def install():
    inarytools.dosed("inxi", "os-release", "sulin-release")
    inarytools.dosed("inxi", "lackware-version SuSE-release", "lackware-version SuSE-release sulin-release")
    inarytools.dobin("inxi")
    inarytools.doman("inxi.1.gz")
    inarytools.dodoc("inxi.changelog")
    
    inarytools.dosym("/usr/bin/inxi", "/usr/share/kde4/apps/konversation/scripts/inxi")
