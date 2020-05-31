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

# Inary Modules
import inary.db
import inary.ui
import inary.uri
import inary.data
import inary.file
import inary.errors
import inary.util as util
import inary.context as ctx

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


@util.locked
def add_repo(name, indexuri, at=None):
    import re
    if not re.match(r"^[0-9{}\-\\_\\.\s]*$".format(str(util.letters())), name):
        raise inary.errors.Error(_('Not a valid repository name.'))
    repodb = inary.db.repodb.RepoDB()
    if repodb.has_repo(name):
        raise inary.errors.Error(
            _('Repository \"{}\" already present.').format(name))
    elif repodb.has_repo_url(indexuri, only_active=False):
        repo = repodb.get_repo_by_url(indexuri)
        raise inary.errors.Error(
            _('Repository \"{}\" already present with name \"{}\".').format(
                name, repo))
    else:
        repo = inary.db.repodb.Repo(inary.uri.URI(indexuri))
        repodb.add_repo(name, repo, at=at)
        ctx.ui.info(_('Flushing database caches...'), verbose=True)
        inary.db.flush_caches()
        ctx.ui.info(_('Repository \"{}\" added to system.').format(name))


@util.locked
def remove_repo(name):
    repodb = inary.db.repodb.RepoDB()
    if repodb.has_repo(name):
        repodb.remove_repo(name)
        ctx.ui.info(_('Flushing database caches...'), verbose=True)
        inary.db.flush_caches()
        ctx.ui.info(_('Repository \"{}\" removed from system.').format(name))
    else:
        raise inary.errors.Error(
            _('Repository \"{}\" does not exist. Cannot remove.').format(name))


@util.locked
def set_repo_activity(name, active):
    """
    Changes the activity status of a  repository. Inactive repositories will have no effect on
    upgrades and installs.
    @param name: name of the repository
    @param active: the new repository status
    """
    repodb = inary.db.repodb.RepoDB()
    if active:
        repodb.activate_repo(name)
    else:
        repodb.deactivate_repo(name)
    ctx.ui.info(_('Regenerating database caches...'), verbose=True)
    inary.db.regenerate_caches()


@util.locked
def update_repos(repos, force=False):
    inary.db.historydb.HistoryDB().create_history("repoupdate")
    updated = False
    try:
        for repo in repos:
            updated |= __update_repo(repo, force)
    finally:
        if updated:
            ctx.ui.info(_('Regenerating database caches...'), verbose=True)
            inary.db.regenerate_caches()


@util.locked
def update_repo(repo, force=False):
    inary.db.historydb.HistoryDB().create_history("repoupdate")
    updated = __update_repo(repo, force)
    if updated:
        ctx.ui.info(_('Regenerating database caches...'), verbose=True)
        inary.db.regenerate_caches()


def __update_repo(repo, force=False):
    ctx.ui.status(
        _('Updating package repository: \"{}\"').format(repo),
        push_screen=False)
    ctx.ui.notify(inary.ui.updatingrepo, name=repo)
    repodb = inary.db.repodb.RepoDB()
    index = inary.data.index.Index()
    if repodb.has_repo(repo):
        repouri = repodb.get_repo(repo).indexuri.get_uri()
        try:
            index.read_uri_of_repo(repouri, repo)
        except inary.file.AlreadyHaveException:
            ctx.ui.info(
                _('\"{}\" repository information is up-to-date.').format(repo))
            if force:
                ctx.ui.info(_('Updating database at any rate as requested.'))
                index.read_uri_of_repo(repouri, repo, force=force)
            else:
                return False

        inary.db.historydb.HistoryDB().update_repo(repo, repouri, "update")

        repodb.check_distribution(repo)

        try:
            index.check_signature(repouri, repo)
        except inary.file.InvalidSignature as e:
            ctx.ui.info(_("Repository \"{}\" is deactivated because of GPG Signature fail.").format(repo),
                        color='brightyellow')
            set_repo_activity(repo, False)
            ctx.ui.warning(e)

        ctx.ui.info(_('Package database updated.'))
    else:
        raise inary.errors.Error(
            _('No repository named \"{}\" found.').format(repo))

    return True
