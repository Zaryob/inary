.. -*- coding: utf-8 -*-

================
inary rebuild-db
================

`inary rebuild-db` command is used to rebuilding all databases including :term:`filesdb`

.. note:: This operation needs privileges and can be allowed by only super user.

**Using**
---------
.. code-block:: shell

          sh ~# inary rdb
          sh ~# inary rebuild-db

**Options**
-----------

rebuild-db options:
         -f, --files                 Rebuild files database


**Example Runtime Output**
--------------------------

.. code-block:: shell

        sh ~# inary rebuild-db
        Rebuild INARY databases? (yes/no):  y
        Creating files database...
        Adding files of "expat" package to database...
        Added files database...
