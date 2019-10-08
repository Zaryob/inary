.. -*- coding: utf-8 -*-

===========
inary blame
===========

`inary blame` gives information of packager name and email from :term:`installdb` or package file.
 `blame` operation gives information under history tag rather than giving detailed information


**Using**
---------

.. code-block:: shell

          sh ~$ inary blame <package-name or package-file>
          sh ~$ inary bl <package-name or package-file>


**Options**
--------------

blame options:

            -r, --release     Blame for the given release

            -a, --all         Blame for the given release


**Example Runtime**
-----------------------------

.. code-block:: shell

            $ inary blame expat
            Name: expat, version: 2.2.6, release: 1
            Package Maintainer: Süleyman POYRAZ <zaryob.dev@gmail.com>
            Release Updater: Süleyman POYRAZ <zaryob.dev@gmail.com>
            Update Date: 2018-12-23

            First release
