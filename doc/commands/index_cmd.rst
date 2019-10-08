.. -*- coding: utf-8 -*-

===========
inary index
===========

`inary index` command creates an index file of repository. This command collects \
all informations in :term:`pspec.xml` and :term:`metadata.xml` from binary packages \
then accumulates this informations as an index file.

`index` operation creates index files from both of source packages and binary packages. \
But filtering is also possible.

**Using**
---------

`index` operation creates index from one directory if the argument is given...

.. code-block:: shell

          sh ~$ inary index <directory>
          sh ~$ inary ix <directory>

...but indexes all tree on working directory if no argument is given.

.. code-block:: shell

          sh ~$ inary index
          sh ~$ inary ix

**Options**
-----------
index options
          -a, --absolute-urls         Store absolute links for indexed files.
          -o, --output                Index output file
          --compression-types         Comma-separated compression types for index file
          --skip-sources              Do not index INARY spec files.
          --skip-signing              Do not sign index.

**Example Runtime Output**
--------------------------

.. code-block:: shell

          sh ~# inary graph



.. code-block:: shell

          sh ~$ inary ix
          Building index of Inary files under "."

          * Generating index tree...

           * Adding "components.xml" to index
           * Adding "distribution.xml" to index
           * Adding "groups.xml" to index

           * Adding binary packages:
             * Adding packages from directory "a"... done.
             * Adding packages from directory "b"... done.
             * Adding packages from directory "c"... done.
             * Adding packages from directory "d"... done.
             * Adding packages from directory "e"... done.
             * Adding packages from directory "f"... done.
             * Adding packages from directory "g"... done.
             * Adding packages from directory "h"... done.
             * Adding packages from directory "i"... done.
             * Adding packages from directory "j"... done.
             * Adding packages from directory "k"... done.
             * Adding packages from directory "l"... done.
             * Adding packages from directory "liba"... done.
             * Adding packages from directory "libb"... done.
             * Adding packages from directory "libc"... done.
             * Adding packages from directory "libd"... done.
             * Adding packages from directory "libe"... done.
             * Adding packages from directory "libf"... done.
             * Adding packages from directory "libg"... done.
             * Adding packages from directory "libi"... done.
             * Adding packages from directory "libj"... done.
             * Adding packages from directory "libk"... done.
             * Adding packages from directory "libl"... done.
             * Adding packages from directory "libm"... done.
             * Adding packages from directory "libn"... done.
             * Adding packages from directory "libo"... done.
             * Adding packages from directory "libp"... done.
             * Adding packages from directory "libq"... done.
             * Adding packages from directory "libr"... done.
             * Adding packages from directory "libs"... done.
             * Adding packages from directory "libt"... done.
             * Adding packages from directory "libu"... done.
             * Adding packages from directory "libv"... done.
             * Adding packages from directory "libw"... done.
             * Adding packages from directory "libx"... done.
             * Adding packages from directory "liby"... done.
             * Adding packages from directory "m"... done.
             * Adding packages from directory "n"... done.
             * Adding packages from directory "o"... done.
             * Adding packages from directory "p"... done.
             * Adding packages from directory "q"... done.
             * Adding packages from directory "r"... done.
             * Adding packages from directory "s"... done.
             * Adding packages from directory "t"... done.
             * Adding packages from directory "u"... done.
             * Adding packages from directory "v"... done.
             * Adding packages from directory "w"... done.
             * Adding packages from directory "x"... done.
             * Adding packages from directory "y"... done.
             * Adding packages from directory "z"... done.
          * Writing index file.
          * Index file written.
