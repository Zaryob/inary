.. -*- coding: utf-8 -*-

In the previous section, I explained how to add the repository to install the package. I continue assuming \
that you have `try_repo` on your system.

===========================================
Package Installing and Upgrading Operations
===========================================


How to install a new package?
-----------------------------

We can do the package installation in two different types: installation from binary package and compilation from source package. In this part we will try to deal with binary packages.

But if you have a .inary file, installion is one command away:

.. code-block:: shell

          sh ~# inary it dummy-0.0.1-1-s19-x86_64.inary
          Installing [ 1 / 1 ]
          Installing "dummy", version 0.0.1, release 1
          Extracting the files of "dummy"
          Adding files of "dummy" package to database...
          Installed "dummy"

But you have to meet all the dependencies. So you need to use repositories to install packages.

Where can I see the all packages in repositories?
-------------------------------------------------

list-available (as a short format la) command is used for this works.

.. code-block:: shell

          sh ~# inary la 
          Installed packages are shown in this color.

            Repository : "try_repo"

          ConsoleKit                               - A framework for defining and tracking users, login sessions, and seats
          ConsoleKit-dbginfo                       - Debug files for ConsoleKit
          ConsoleKit-devel                         - Development files for ConsoleKit
          .....
          ....
          ...
          ..
          .

It pushes all available packages on all available repositories. It gives tons of package name and summary in that output. 


How do I find the right package?
--------------------------------

Inary provides searching of package names from packagedb. In doing so, it has a package infrastructure that performs compliance analysis. In other words, it lists not only exactly matching packages but also nearby packages.

.. code-block:: shell

          sh ~# inary sr openrc
          eudev-pages       = Man pages for eudev package.
          eudev-devel       = Development files for eudev
          eudev-32bit       = 32-bit shared libraries for eudev
          eudev             = eudev is a fork of system-udev
          eudev-docs        = Documentation for eudev package.
          openrc-docs       = Documentation for openrc package.
          openrc-dbginfo    = Debug files for openrc
          openrc            = Dependency based init system that works with sysvinit.
          openrc-pages      = Man pages for openrc package.
          openresolv        = A framework for managing DNS information.
          openrc-tmpfiles   = Lime GNU/ Linux service scripts for openrc

However, if the said package is not found, it doesn't give any output.

.. code-block:: shell

          sh ~# inary sr systemd

As you see.


How do I install it?
--------------------

install command with package-name parameter is used in order to install packages. Multiple packages can be installed by separating the package names by a space.

.. code-block:: shell

          sh ~# inary it openrc
          Total size of package(s): 0.00  B / 6.54 KB
          After this operation, 13.00 KB space will be used.
          Downloading [ 1 / 1 ] => [openrc]
          Creating files database...
          Added files database...
          Installing [ 1 / 1 ]
          Installing "openrc", version 1.4.5, release 2
          Extracting the files of "openrc"
          Adding files of "openrc" package to database...
          Installed "openrc"


Where can I see the installed packages?
---------------------------------------

list-installed (as a short format li) command is used for this works.

.. code-block:: shell

          sh ~# inary li 
          acl      - Access control list utilities.
          ...
          ...
          ...
          openrc   - Dependency based init system that works with sysvinit.
          ...
          ..
          .

Openrc is added in our installed list.


Where are newests packages?
---------------------------

The packages of our system are constantly updated. list-newests is used to analyze newest packages added to \
repository.

.. code-block:: shell

          sh ~# inary ln
          Packages added to 'try_repo':
          python-ply  - Implementation of lex and yacc parsing tools for Python.
          python3-ply - Implementation of lex and yacc parsing tools for Python.

list-upgrades is used to upgradable packages in repositories.

.. code-block:: shell

          sh ~# inary lu
          openrc   - Dependency based init system that works with sysvinit.


How can I upgrade newests packages?
-----------------------------------

.. code-block:: shell

          sh ~# inary up
          Updating repositories.
          Updating package repository: "try_repo"
          Package database updated.
          The following packages will be upgraded:
          colorgcc
          Total size of package(s): 6.54 KB / 6.54 KB
          After this operation, 0.00  B space will be used.
          Downloading [ 1 / 1 ] => [colorgcc]
          Creating files database...
          -> Adding files of "colorgcc" package to db...
          Added files database...
          Installing [ 1 / 1 ]
          Installing "colorgcc", version 1.4.5, release 2
          Upgrading to new upstream version.
          Extracting the files of "colorgcc"
          Adding files of "colorgcc" package to database...
          Upgraded "colorgcc"


How can I downgrade packages whether they are broken?
-----------------------------------------------------

It is working on progress.
