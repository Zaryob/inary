#/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/licenses/gpl.txt

from inary.actionsapi import get
from inary.actionsapi import autotools
from inary.actionsapi import inarytools
from inary.actionsapi import shelltools

WorkDir = "."
WORKDIR = "%s/%s-%s" % (get.workDIR(), get.srcNAME(), get.srcVERSION())
NCURSES = "ncurses-build"
NCURSESW = "ncursesw-build"
CONFIGPARAMS = "--without-debug \
                --with-shared \
                --with-normal \
                --without-profile \
                --disable-rpath \
                --enable-const \
                --enable-largefile \
                --with-terminfo-dirs='/etc/terminfo:/usr/share/terminfo' \
                --disable-termcap \
                --enable-hard-tabs \
                --enable-xmc-glitch \
                --enable-colorfgbg \
                --with-rcs-ids \
                --with-mmask-t='long' \
                --without-ada \
                --enable-symlinks \
                --without-gpm"

def setup():
    shelltools.makedirs(NCURSES)
    shelltools.makedirs(NCURSESW)
    shelltools.cd(NCURSESW)

    global CONFIGPARAMS

    if get.buildTYPE() == "_emul32":
        inarytools.flags.add("-m32")
        inarytools.ldflags.add("-m32")
        shelltools.export("PKG_CONFIG_LIBDIR", "/usr/lib32/pkgconfig")
        inarytools.dosed("%s/misc/gen-pkgconfig.in" % WORKDIR, "^(show_prefix=).*", "\\1'/usr'")
        CONFIGPARAMS += " --prefix=/_emul32 \
                          --libdir=/usr/lib32 \
                          --libexecdir=/_emul32/lib \
                          --bindir=/_emul32/bin \
                          --sbindir=/_emul32/sbin \
                          --mandir=/_emul32/share/man"
    else:
        CONFIGPARAMS += " --prefix=/usr \
                          --libdir=/usr/lib \
                          --libexecdir=/usr/lib \
                          --bindir=/usr/bin \
                          --sbindir=/usr/sbin \
                          --mandir=/usr/share/man"

    shelltools.system("%s/configure --enable-widec --enable-pc-files %s" % (WORKDIR, CONFIGPARAMS))


def build():
    global CONFIGPARAMS
    shelltools.cd(NCURSESW)
    autotools.make()
    if not get.buildTYPE() == "_emul32" and get.ARCH() == "x86_64": CONFIGPARAMS += " --with-chtype=long"
    shelltools.cd("../%s" % NCURSES)
    shelltools.system("%s/configure %s" % (WORKDIR, CONFIGPARAMS))
    autotools.make()

def install():
    shelltools.cd(NCURSESW)
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    LIB = "/usr/lib32" if get.buildTYPE() == "_emul32" else "/usr/lib"
    print (LIB)
    for lib in ["ncurses", "form", "panel", "menu"]:
        shelltools.echo("lib%s.so" % lib, "INPUT(-l%sw)" % lib)
        inarytools.dolib_so("lib%s.so" % lib, destinationDirectory = LIB)
        inarytools.dosym("lib%sw.a" % lib, "%s/lib%s.a" % (LIB, lib))
    inarytools.dosym("libncurses++w.a", "%s/libncurses++.a" % LIB)
    for lib in ["ncurses", "ncurses++", "form", "panel", "menu"]:
        inarytools.dosym("%sw.pc" % lib, "%s/pkgconfig/%s.pc" % (LIB, lib))

    shelltools.echo("libcursesw.so", "INPUT(-lncursesw)")
    inarytools.dolib_so("libcursesw.so", destinationDirectory = LIB)
    inarytools.dosym("libncurses.so", "%s/libcurses.so" % LIB)
    inarytools.dosym("libncursesw.a", "%s/libcursesw.a" % LIB)
    inarytools.dosym("libncurses.a", "%s/libcurses.a" % LIB)

    #for fix 
    inarytools.dosym("libncursesw.so.6.0", "%s/libncursesw.so.5" % LIB)
    inarytools.dosym("libncurses.so.6.0", "%s/libncurses.so.5" % LIB)
    inarytools.dosym("libpanelw.so.6.0", "%s/libpanelw.so.5" % LIB)
    inarytools.dosym("libformw.so.6.0", "%s/libformw.so.5" % LIB)
    inarytools.dosym("libmenuw.so.6.0", "%s/libmenuw.so.5" % LIB)

    shelltools.cd("../%s" % NCURSES)
    for lib in ["ncurses", "form", "panel", "menu"]:
        inarytools.dolib_so("lib/lib%s.so.%s" % (lib, get.srcVERSION()), destinationDirectory = LIB)
        inarytools.dosym("lib%s.so.%s" % (lib, get.srcVERSION()), "%s/lib%s.so.6" % (LIB, lib))

    if get.buildTYPE() == "_emul32":
        inarytools.removeDir("/_emul32")
        return

    shelltools.cd(WORKDIR)
    shelltools.system("grep -B 100 '$Id' README > license.txt")
    inarytools.dodoc("ANNOUNCE", "NEWS", "README*", "TO-DO", "license.txt")
