.. -*- coding: utf-8 -*-

.. _glossary:

Glossary
========

.. glossary::

    installdb
      One of the database used in inary. In this database is created automatically with information of installed packages, their files, their dependency and provides

    filesdb
      One of database used in inary. In this database is created first run of inary and updates regulary. It contains files' paths, sha1sum and permissions of packages.

    pspec.xml
      This file is a part of source packages. It contains specific details about package.

    actions.py
      This file is instruction of building.

    metadata.xml
      This file generates automatically from :term:`pspec.xml`. It includes some details under Package tag in :term:`pspec.xml`.

    files.xml
      This file contains all details about files which included in package.
