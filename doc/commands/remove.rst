.. -*- coding: utf-8 -*-

============
inary remove
============

`inary remove` is the command to remove the package from the system.

.. note:: This operation needs privileges and can be allowed by only super user.

**Using**
---------

.. code-block:: shell

          sh ~$ inary remove <package-name>
          sh ~$ inary rm <package-name>


**Options**
--------------

remove options:
          --ignore-dependency          Do not take dependency information into account.
          --ignore-safety              Bypass safety switch.
          --ignore-scom                Bypass scom configuration agent.
          -n, --dry-run                Do not perform any action, just show what would be done.
          --purge                      Removes everything including changed config files of the package.
          -c, --component              Remove component's and recursive components' packages.


**Example Runtime**
-----------------------------

.. code-block::

            sh ~$ inary rm mjpegtools
            The following list of packages will be removed in the respective order to satisfy dependencies:
            gst-plugins-bad-dbginfo gst-plugins-bad-devel gst-plugins-bad mjpegtools-devel
            Removing "gst-plugins-bad-dbginfo"
            Removing files of "gst-plugins-bad-dbginfo" package from database...
            Removing files of "gst-plugins-bad-dbginfo" package from system...
            Removed "gst-plugins-bad-dbginfo"
            Removing "gst-plugins-bad-devel"
            Removing files of "gst-plugins-bad-devel" package from database...
            Removing files of "gst-plugins-bad-devel" package from system...
            Removed "gst-plugins-bad-devel"
            Removing "gst-plugins-bad"
            Removing files of "gst-plugins-bad" package from database...
            Removing files of "gst-plugins-bad" package from system...
            Removed "gst-plugins-bad"
            Removing "mjpegtools-devel"
            Removing files of "mjpegtools-devel" package from database...
            Removing files of "mjpegtools-devel" package from system...
            Removing "mjpegtools"
            Removing files of "mjpegtools" package from database...
            Removing files of "mjpegtools" package from system...
