.. -*- coding: utf-8 -*-

=============
inary upgrade
=============

`inary upgrade` command allows to upgrade new release of installed packages.

**Using**
---------

`upgrade` operation upgrades specific one of package if the argument is given...

.. code-block:: shell

          sh ~$ inary upgrade <package-name>
          sh ~$ inary up <package-name>

...but upgrades all new releases if no argument is given.


.. code-block:: shell

          sh ~$ inary upgrade
          sh ~$ inary up

**Options**
--------------

upgrade options:
          --ignore-dependency           Do not take dependency information into account.
          --ignore-safety               Bypass safety switch.
          --ignore-scom                 Bypass scom configuration agent.
          -n, --dry-run                 Do not perform any action, just show what would be done.
          --security-only               Security related package upgrades only.
          -b, --bypass-update-repo      Do not update repositories.
          --ignore-file-conflicts       Ignore file conflicts.
          --ignore-package-conflicts    Ignore package conflicts.
          -c, --component               Upgrade component's and recursive components' packages.
          -r, --repository              Name of the to be upgraded packages' repository.
          -f, --fetch-only              Fetch upgrades but do not install.
          -x, --exclude                 When upgrading system, ignore packages and components whose basenames match pattern.
          --exclude-from                When upgrading system, ignore packages and components whose basenames match any pattern contained in file.
          -s, --compare-sha1sum         Compare sha1sum repo and installed packages.


**Example Runtime**
-----------------------------

.. code-block::

          sh ~# inary up
          Updating repositories.
          Updating package repository: "core"
          No signature found for "/repo/SulinRepository/inary-index.xml"
          Package database updated.
          Checking dependencies for install...
          The following packages will be upgraded:
          libsoup  libsoup-devel
          Total size of package(s): 0.00  B / 410.70 KB
          After this operation, -4160.00  B space will be freed.
          Downloading 1 / 2
          Package "libsoup" found in repository "core"
          Downloading 2 / 2
          Package "libsoup-devel" found in repository "core"
          Installing 1 / 2
          Installing "libsoup", version 2.68.1, release 2
          Upgrading to new distribution release.
          Extracting the files of "libsoup"
          Removing files of "libsoup" package from database...
          Adding files of "libsoup" package to database...
          Upgraded "libsoup"
          Installing 2 / 2
          Installing "libsoup-devel", version 2.68.1, release 2
          Upgrading to new distribution release.
          Extracting the files of "libsoup-devel"
          Removing files of "libsoup-devel" package from database...
          Adding files of "libsoup-devel" package to database...
          Upgraded "libsoup-devel"
