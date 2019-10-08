.. -*- coding: utf-8 -*-

===========
inary fetch
===========

`inary fetch` is used to download packages from the repository. It fetchs binary packages to
working directory

**Using**
---------

.. code-block:: shell

          sh ~$ inary fetch <package-name>
          sh ~$ inary fc <package-name>


**Options**
--------------

fetch options:
          -o, --output-dir             Output directory for the fetched packages
          --runtime-deps               Download with runtime dependencies.

**Example Runtime**
-----------------------------

.. code-block:: shell

          sh ~$ inary fc expat
          "expat" package found in "core" repository.
          expat-2.2.7-2-s19-x86_64.inary (194.0 KB)
