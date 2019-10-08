.. -*- coding: utf-8 -*-

==================
inary delete-cache
==================

`inary delete-cache` allows to clean inary's temporary files package and source code archives. It does not take any other argument, or parameter.

.. note:: This operation needs privileges and can be allowed by only super user.

**Using**
---------

.. code-block:: shell

          sh ~# inary dc
          sh ~# inary delete-cache

**Example Runtime Output**
--------------------------

.. code-block:: shell

        sh ~# inary delete-cache
        Cleaning package cache "/var/cache/inary/packages"...
        Cleaning source archive cache "/var/cache/inary/archives"...
        Cleaning temporary directory "/var/inary"...
        Removing cache file "/var/cache/inary/packagedb.cache"...
        Removing cache file "/var/cache/inary/sourcedb.cache"...
        Removing cache file "/var/cache/inary/componentdb.cache"...
        Removing cache file "/var/cache/inary/groupdb.cache"...
