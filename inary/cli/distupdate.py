# -*- coding:utf-8 -*-
#
# Copyright (C) 2016 - 2017,  Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import optparse

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary.cli.command as command
import inary.context as ctx
import inary.reactor as Reactor
import inary.db

class DistUpdate(command.PackageOp, metaclass=command.autocommand):
    __doc__ = _("""Update the system a new release

Usage: DistUpdate [ next_dist_release_repo_url ] [ dist-update-list ]

                WARNING: DIST-UPDATE risk içerir.
    Dist-Update yapmadan önce iki kez düşününüz. Çünkü
    Dist-Update sonrası sisteminiz çalışmayabilir, tüm
    dosyalarınızı kaybedebilirsiniz. 

   Sisteminizi Dist-Update yapmadan önce yedekleyiniz ve
   EĞER YAPMAK İSTEDİĞİNİZE GERÇEKTEN EMİNSENİZ BU İŞLEMİ
   BAŞLATINIZ.

                OLUŞAN HİÇBİR DİSK VE SİSTEM
                 HASARINDAN SULIN TOPLULUĞU 
                       MESUL DEĞİLDİR

""")

    def __init__(self, args):
        super(DistUpdate, self).__init__(args)

    name = ("dist-update", "distup")

    def options(self):
        group = optparse.OptionGroup(self.parser, _("dist-update options"))

        super(Upgrade, self).options(group)
        group.add_option("--security-only", action="store_true",
                     default=False, help=_("Security related package upgrades only"))
        group.add_option("-x", "--exclude", action="append",
                     default=None, help=_("When upgrading system, ignore packages and components whose basenames match pattern."))
        group.add_option("--exclude-from", action="store",
                     default=None,
                     help=_("When upgrading system, ignore packages "
                            "and components whose basenames match "
                            "any pattern contained in file."))
        group.add_option("-s", "--compare-sha1sum", action="store_true",
                     default=False, help=_("compare sha1sum repo and installed packages"))

        self.parser.add_option_group(group)

    def run(self):
        self.init()
        argv = []
        argv.extend(self.args)
        targetrepo = argv[1]
        Reactor.distupdate(targetrepo)
