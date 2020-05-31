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

# Standart Python Modules
import os

# Inary Modules
import inary.util
import inary.context as ctx
import inary.db.lazydb as lazydb
import inary.data.history as History


class HistoryDB(lazydb.LazyDB):

    # noinspection PyArgumentList
    def init(self):
        self.__logs = self.__generate_history()
        self.history = History.History()

    @staticmethod
    def __generate_history():
        logs = [
            x for x in os.listdir(
                ctx.config.history_dir()) if x.endswith(".xml")]
        # logs.sort(key=lambda x,y:int(x.split("_")[0]) - int(y.split("_")[0]))
        logs.sort(key=lambda x: int(x.split("_")[0].replace("0o", "0")))
        logs.reverse()
        return logs

    def create_history(self, operation):
        self.history.create(operation)

    def add_and_update(self, pkgBefore=None, pkgAfter=None,
                       operation=None, otype=None):
        self.add_package(pkgBefore, pkgAfter, operation, otype)
        self.update_history()

    def add_package(self, pkgBefore=None, pkgAfter=None,
                    operation=None, otype=None):
        self.history.add(pkgBefore, pkgAfter, operation, otype)

    @staticmethod
    def load_config(operation, package):
        config_dir = os.path.join(
            ctx.config.history_dir(), "%03d" %
            operation, package)
        if os.path.exists(config_dir):
            import distutils.dir_util as dir_util
            dir_util.copy_tree(config_dir, "/")

    def save_config(self, package, config_file):
        hist_dir = os.path.join(
            ctx.config.history_dir(),
            self.history.operation.no,
            package)
        if os.path.isdir(config_file):
            os.makedirs(os.path.join(hist_dir, config_file))
            return

        destdir = os.path.join(hist_dir, config_file[1:])
        inary.util.copy_file_stat(config_file, destdir)

    def update_repo(self, repo, uri, operation=None):
        self.history.update_repo(repo, uri, operation)
        self.update_history()

    def update_history(self):
        self.history.update()

    def get_operation(self, operation):
        for log in self.__logs:
            if log.startswith("%03d_" % operation):
                hist = History.History(os.path.join(
                    ctx.config.history_dir(), log))
                hist.operation.no = int(log.split("_")[0].replace("0o", "0"))
                return hist.operation
        return None

    @staticmethod
    def get_package_config_files(operation, package):
        package_path = os.path.join(
            ctx.config.history_dir(), "%03d/%s" %
            (operation, package))
        if not os.path.exists(package_path):
            return None

        configs = []
        for root, dirs, files in os.walk(package_path):
            for f in files:
                configs.append(("{0}/{1}".format(root, f)))

        return configs

    def get_config_files(self, operation):
        config_path = os.path.join(
            ctx.config.history_dir(),
            "%03d" %
            operation)
        if not os.path.exists(config_path):
            return None

        allconfigs = {}
        packages = os.listdir(config_path)
        for package in packages:
            allconfigs[package] = self.get_package_config_files(
                operation, package)

        return allconfigs

    def get_till_operation(self, operation):
        if not [x for x in self.__logs if x.startswith("%03d_" % operation)]:
            return

        for log in self.__logs:
            if log.startswith("%03d_" % operation):
                return

            hist = History.History(os.path.join(ctx.config.history_dir(), log))
            hist.operation.no = int(log.split("_")[0].replace("0o", "0"))
            yield hist.operation

    def get_last(self, count=0):
        count = count or len(self.__logs)
        for log in self.__logs[:count]:
            hist = History.History(os.path.join(ctx.config.history_dir(), log))
            hist.operation.no = int(log.split("_")[0].replace("0o", "0"))
            yield hist.operation

    def get_last_repo_update(self, last=1):
        repoupdates = [l for l in self.__logs if l.endswith("repoupdate.xml")]
        repoupdates.reverse()

        if last != 1 and len(repoupdates) <= last:
            return None

        hist = History.History(os.path.join(
            ctx.config.history_dir(), repoupdates[-last]))
        return hist.operation.date
