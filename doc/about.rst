.. -*- coding: utf-8 -*-

%%%%%%%%%%%%%%%%%%%%
About Inary Software
%%%%%%%%%%%%%%%%%%%%

`PiSi` fork: Copyright (C) 2005 - 2011, Tubitak / UEKAE
          Licensed with GNU / General Public License version 2.

Inary fork and enhancements: Copyright (C) 2016 - 2018 Suleyman POYRAZ (Zaryob)
          License has been upgraded to version 3 of the GNU / General Public License.

.. _Pisi: https://github.com/Pardus-Linux/pisi

Bifurcated from https://github.com/Pardus-Linux/pisi

Inary package management system started to work on the pisi fork on 21-12-2016 in order \
to repair the deficiencies and errors of the existing pisi package manager and to port it \
to python3 to catch up with the latest developments in Python Programming language;
The first pisi fork (spam) was separated from the fork in terms of coding method and additional \
modules used and turned into a unique one. The name of the library has been changed from \
pisi to inary. The reason for this is to avoid conflicts with linux distributions that \
use similar infrastructure, such as `Solus`_ and  `PisiLinux`_.

.. _Solus: https://dev.sol.us/
.. _PisiLinux: https://www.pisilinux.org

The software was called inary and was made available to the public through the `gitlab`_ and `github`_ \
when it provided the appropriate conditions for the end users.

.. _github: https://github.com/SulinOS
.. _gitlab: https://gitlab.com/SulinOS



What distinguishes it from other package management systems:

  * Has dynamic file database. It is easy to follow up whether there is a change in the installed files.
  * Compared to other package managers coded with Python, it is quite fast.
  * Since all the installation script consists of python script. Since the other data of the package is stored in xml files, package building steps can be done without without entering tons of code.
  * Post-package and post-package operations (postinstall) do not cause any process confusion by separate software.


Other features:
  * It is robust and fast because it works with a database embedded in python.
  * Because it uses LZMA and XZ compression methods, it has smaller packages.
  * Simple and high-level operations with the same determination
  * It includes an API suitable for designing forend applications.
  * Terminal interface is very understandable and user-friendly.
