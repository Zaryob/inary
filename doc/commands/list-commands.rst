.. -*- coding: utf-8 -*-

=======================
Other Commands in INARY
=======================


**inary list-available**
========================

`inary list-available` commands allows to see installable packages in added repositories.

**Using**
---------

.. code-block:: shell

          sh ~# inary list-available
          sh ~# inary la


**Options**
-----------

list-available:
          -l, --long                  Show in long format
          -c, --component             List available packages under given component
          -U, --uninstalled           Show uninstalled packages only


**inary list-sources**
======================

`inary list-sources` commands allows to see source packages in added repositories.

**Using**
---------
.. code-block:: shell

          sh ~# inary list-sources
          sh ~# inary ls


**Options**
-----------

list-sources options:
          -l, --long                Show in long format


**inary list-newest**
=====================

`inary list-newest` commands allows to lastest added/updated packages in added repositories.

**Using**
---------
.. code-block:: shell

            sh ~# inary list-newest
            sh ~# inary ln


**Options**
-----------
list-newest options:
            -s, --since                 List new packages added to repository after this given date formatted as yyyy-mm-dd.
            -l, --last                  List new packages added to repository after last nth previous repository update.


**inary list-upgrades**
=======================

`inary list-upgrades` commands allows to upgrade-able packages in added repositories.

**Using**
---------
.. code-block:: shell

            sh ~# inary list-upgrades
            sh ~# inary lu

**Options**
-----------
list-upgrades options:
            -l, --long                  Show in long format.
            -c, --component             List upgradable packages under given component.
            -i, --install-info          Show detailed install info.


**inary list-installed**
========================

`inary list-installed` commands allows to see installed packages in system.

**Using**
---------
.. code-block:: shell

            sh ~# inary list-installed
            sh ~# inary li

**Options**
-----------
list-installed options:
           -b, --with-build-host        Only list the installed packages built by the given host.
           -l, --long                   Show in long format
           -c, --component              List installed packages under given component.
           -i, --install-info           Show detailed install info.


**inary list-repo**
===================

`inary list-repo` commands allows to added repositories and their information in system.

**Using**
---------
.. code-block:: shell

            sh ~# inary list-repo
            sh ~# inary lr


**inary list-orphaned**
=======================

`inary list-orphaned` commands allows to see orphaned packages in system.

**Using**
---------
.. code-block:: shell

            sh ~# inary list-orphaned
            sh ~# inary lo

**Options**
-----------
list-orphaned options:
            -a, --all                    Show all packages without reverse dependencies.
            -x, --exclude                Ignore packages and components whose basenames match pattern.


**inary list-components**
=========================

`inary list-components` commands allows to see components in repositories.

**Using**
---------
.. code-block:: shell

            sh ~# inary list-components
            sh ~# inary lc

**Options**
-----------
list-components options:
             -l, --long                  Show in long format
             -r, --repository            Name of the source or package repository
