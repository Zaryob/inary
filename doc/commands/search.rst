.. -*- coding: utf-8 -*-

============
inary search
============

`inary search` command allows to search from package names and summary.

**Using**
---------

.. code-block:: shell

          sh ~$ inary search <package-name>
          sh ~$ inary sr <package-name>


**Options**
--------------

search options:
          -l, --language                Summary and description language.
          -r, --repository              Name of the source or package repository.
          -i, --installdb               Search in installdb.
          -s, --sourcedb                Search in sourcedb.
          -c, --case-sensitive          Case sensitive search.
          --name                        Search in the package name.
          --summary                     Search in the package summary.
          --description                 Search in the package description.



**Example Runtime**
-----------------------------

.. code-block:: 

          sh ~$ inary search expa
          expat           - XML parsing libraries
          expat-32bit     - 32-bit shared libraries for expat
          expat-devel     - Development files for expat
          expat-docs      - Documentation for expat package.
          expat-pages     - ManPages for expat package.
          perl-XML-Parser - A Perl extension interface to James Clark's XML parser, expat
