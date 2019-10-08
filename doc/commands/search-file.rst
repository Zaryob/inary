.. -*- coding: utf-8 -*-

=================
inary search-file
=================

`inary search-file` command is used to search files from :term:`installdb`. It allows us \
to determine which package contains a given filename. It allows regex inside of it. So, \
just one keyword is enough to searching, in order to allows regex script.

**Using**
---------

.. code-block:: shell

          sh ~$ inary search-file <file-name>
          sh ~$ inary sf <file-name>


**Options**
--------------

search-file options:
          -l, --long                   Show in long format.
          -q, --quiet                  Show only package name.


**Example Runtime**
-----------------------------

.. code-block:: 

        sh ~$ inary search-file expat.h
        Searching for "expat.h"
        Package "expat-devel" has file "/usr/include/expat.h"
        Package "python3-devel" has file "/usr/include/python3.7m/pyexpat.h"
        Package "python-devel" has file "/usr/include/python2.7/pyexpat.h"
