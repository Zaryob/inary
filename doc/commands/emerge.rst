.. -*- coding: utf-8 -*-

============
inary emerge
============

`inary emerge` command is used to build a source package from the source repository and to install the system.

.. note:: This operation needs privileges and can be allowed by only super user.

**Using**
---------
`emerge` operation takes an argument which is source package name.

.. code-block:: shell

          sh ~# inary emerge <package-name>
          sh ~# inary em <package-name>

**Options**
-----------

emerge options:
          -c, --component              Emerge available packages under given component
          --ignore-file-conflicts      Ignore file conflicts.
          --ignore-package-conflicts   Ignore package conflicts.
          --ignore-scom                Bypass scom configuration agent.



**Example Runtime Output**
--------------------------

.. code-block:: shell

        sh ~$ inary emerge expat
        Building source package: "expat"
        expat-2.2.6.tar.bz2 [cached]
        >>> Unpacking archive(s)...
         -> (/var/inary/expat-2.2.6-1/work) unpacked.
        >>> Setting up source...
        GNU Config Update Finished.
        GNU Config Update Finished.
        [Running Command]: ./configure                 --prefix=/usr                 --build=x86_64-pc-linux-gnu                 --mandir=/usr/share/man                 --infodir=/usr/share/info                 --datadir=/usr/share                 --sysconfdir=/etc                 --localstatedir=/var                 --libexecdir=/usr/libexec                 --disable-static
        >>> Build source...
        [Running Command]: make -j5
        >>> Installing...
        [Running Command]: make DESTDIR=/var/inary/expat-2.2.6-1/install man1dir=/usr/share/man/man1 install
        [Running Command]: install -m 0644 "doc/expat.png" /var/inary/expat-2.2.6-1/install/usr/share/doc/expat/html
        [Running Command]: install -m 0644 "doc/valid-xhtml10.png" /var/inary/expat-2.2.6-1/install/usr/share/doc/expat/html
        [Running Command]: install -m 0644 "doc/reference.html" /var/inary/expat-2.2.6-1/install/usr/share/doc/expat/html
        [Running Command]: install -m 0644 "doc/style.css" /var/inary/expat-2.2.6-1/install/usr/share/doc/expat/html
        [Running Command]: install -m 0644 "Changes" /var/inary/expat-2.2.6-1/install/usr/share/doc/expat
        [Running Command]: install -m 0644 "README.md" /var/inary/expat-2.2.6-1/install/usr/share/doc/expat
        Removing special "libtool", file: "/var/inary/expat-2.2.6-1/install/usr/lib/libexpat.la"...
        Building package: "expat"
        Creating "expat-2.2.6-1-s19-x86_64.inary"...
        Building package: "expat-devel"
        Creating "expat-devel-2.2.6-1-s19-x86_64.inary"...
        Building package: "expat-docs"
        Creating "expat-docs-2.2.6-1-s19-x86_64.inary"...
        Building package: "expat-pages"
        Creating "expat-pages-2.2.6-1-s19-x86_64.inary"...
        Keeping build directory
        Installing package "expat" version 2.2.6 release 1
        Extracting files of "expat" package.
        Adding files of "expat" to database...
        Installing "expat".
