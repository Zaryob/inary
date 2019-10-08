.. -*- coding: utf-8 -*-

=====================
inary remove-orphaned
=====================

`inary remove-orphaned` allows us to delete packages whose come as a dependency \
of any package then reverse dependencies have been deleted. That is, it automatically \
removes unneeded packages.

.. note:: This operation needs privileges and can be allowed by only super user.

**Using**
---------

.. code-block:: shell

          sh ~$ inary remove-orphaned
          sh ~$ inary ro


**Options**
--------------

remove-orphaned options:
          --ignore-dependency           Do not take dependency information into account.
          --ignore-safety               Bypass safety switch.
          --ignore-scom                 Bypass scom configuration agent.
          -n, --dry-run                 Do not perform any action, just show what would be done.
          -x, --exclude                 When removing orphaned, ignore packages and components whose basenames match pattern.


**Example Runtime**
-----------------------------

.. code-block::

        sh ~$ inary remove-orphaned
        The following list of packages will be removed in the respective order to satisfy dependencies:
        libnut libdc1394
        After this operation, 11.21 MB space will be freed.
        Removing "libnut"
        Removing files of "libnut" package from database...
        Removing files of "libnut" package from system...
        Removed "libnut"
        Removing "libdc1394"
        Removing files of "libdc1394" package from database...
        Removing files of "libdc1394" package from system...
        Removed "libdc1394"
