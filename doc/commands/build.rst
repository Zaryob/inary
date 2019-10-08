.. -*- coding: utf-8 -*-

===========
inary build
===========

`inary build` command  is used to build binary packages from source files. \
Building operation can be made with giving :term:`pspec.xml` path or source name \
whether any source repository have been added.

**Using**
---------

Build command can be used two ways.

.. code-block:: shell

          sh ~$ inary build <pspec-file>
          sh ~$ inary bi <package-file>

and also used with giving source name (unlike emerge, only the package creations happens)

.. code-block:: shell

          sh ~$ inary build <source-package-name>
          sh ~$ inary bi <source-package-name>

**Options**
--------------

build options:
            -q, --quiet                  Run inary build operation without printing extra debug information.
            --ignore-dependency         Do not take dependency information into account.
            -O, --output-dir            Output directory for produced packages.
            --ignore-action-errors      Bypass errors from ActionsAPI.
            --ignore-safety             Bypass safety switch.
            --ignore-check              Bypass testing step.
            --create-static             Create a static package with ar files.
            -F, --package-format        Create the binary package using the given format. Use '-F help' to see a list of supported formats.
            --use-quilt                 Use quilt patch management system instead of GNU patch.
            --ignore-sandbox            Do not constrain build process inside the build folder.

The inary package manager allows you to do the building step by step (each step is specified in the :term:`actions.py` script as a function.) \
If an error occurs in any of these steps, the construction can be resumed from the step left. These step specifications is also given to build \
command as parameters.

Build Steps:
            --fetch                     Break build after fetching the source archive.
            --unpack                    Break build after unpacking the source archive, checking sha1sum and applying patches.
            --setup                     Break build after running configure step.
            --build                     Break build after running compile step.
            --check                     Break build after running check step.
            --install                   Break build after running install step.
            --package                   Create INARY package.

**Example Runtime Output**
--------------------------

.. code-block:: shell

      sh ~$ inary build
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
      *** 0 error, 1 warning
