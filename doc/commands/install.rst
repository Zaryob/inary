.. -*- coding: utf-8 -*-

=============
inary install
=============

`inary install` command is used to installing binary packages from inary file or repository.

.. note:: This operation needs privileges and can be allowed by only super user.

**Using**
---------

.. code-block:: shell

          sh ~# inary install <package-name>
          sh ~# inary it <package-name>


**Options**
--------------

install options:
          --ignore-dependency          Do not take dependency information into account.
          --ignore-safety              Bypass safety switch.
          --ignore-scom                Bypass scom configuration agent.
          -n, --dry-run                Do not perform any action, just show what would be done.
          --reinstall                  Reinstall already installed packages.
          --ignore-check               Skip distribution release and architecture check.
          --ignore-file-conflicts      Ignore file conflicts.
          --ignore-package-conflicts   Ignore package conflicts.
          -c, --component              Install component's and recursive components' packages.
          -r, --repository             Name of the component's repository.
          -f, --fetch-only             Fetch upgrades but do not install.
          -x, --exclude                When installing packages, ignore packages and components whose basenames match pattern.
          --exclude-from               When installing packages, ignore packages and components whose basenames match any pattern contained in file.
          -s, --store-lib-info         Store previous libraries info when package is updating to newer version.


**Example Runtime**
-----------------------------

.. code-block::

          sh ~# inary it gsm
          Checking dependencies for install...
          Total size of package(s): 0.00  B / 93.87 KB
          After this operation, 389.92 KB space will be used.
          Downloading 1 / 1
          Package "gsm" found in repository "core"
          Installing 1 / 1
          Installing "gsm", version 1.0.13, release 1
          Extracting the files of "gsm"
          Adding files of "gsm" package to database...
          Installed "gsm"
