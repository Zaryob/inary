.. -*- coding: utf-8 -*-

===========
inary delta
===========

The `inary delta` command is used to create delta packages from two different release of packages.
It creates a delta package of only the changed files.

This allows us to minimize updates and reduce the data network less regularly.
allows us to use.

.. note:: delta packets are recommended only for packages created from the same version source.

**Using**
---------

.. code-block:: shell

            sh ~$ inary delta <older-release-of-package> <newer-release-of-package>

.. note: Creating `delta` packages are only available with same source packages' different releases. 

**Options**
-----------

delta options:
            -t, --newest-package          Use arg as the new package and treat other arguments as old packages.
            -O, --output-dir              Output directory for produced packages.
            -F, --package-format          Create the binary package using the given format. Use '-F help' to see a list of supported formats.


**Example Runtime Output**
--------------------------

.. code-block:: shell

            sh ~$ inary delta expat-2.2.6-1-s19-x86_64.inary expat-2.2.6-2-s19-x86_64.inary
            Creating delta package: "expat-1-2-s19-x86_64.delta.inary"...
