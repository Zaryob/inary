.. -*- coding: utf-8 -*-

==========
inary info
==========

`inary info` shows detailed information including provides, dependencies, component, etc.
Unlike blame command, it allows us to see all the components written in :term:`pspec.xml`

**Using**
---------

.. code-block:: shell

          sh ~$ inary info <package-name>

**Options**
--------------

info options:
          -f, --files                 Show a list of package files.
          -c, --component             Info about the given component.
          -F, --files-path            Show only paths.
          -s, --short                 Do not show details.
          --xml                       Output in xml format.

**Example Runtime**
-----------------------------

.. code-block:: shell

            sh ~$ ianry info expat
            "expat" package is not installed.
            Package found in "trykl" repository:
            Name                : expat, version: 2.2.7, release: 2
            Summary             : XML parsing libraries
            Description         : This is expat, the C library for parsing XML, written by James Clark. Expat is a stream oriented XML parser. This means that you register handlers with the parser prior
                                  to starting the parse. These handlers are called when the parser discovers the associated structures in the document being parsed. A start tag is an example of the kind
                                  of structures for which you may register handlers.
            Licenses            : as-is
            Component           : system.base
            Provides            :
            Dependencies        :
            Distribution        : Sulin, Dist. Release: 2019
            Architecture        : x86_64, Installed Size: 753.35 KB, Package Size: 193.97 KB, install.tar.xz sha1sum: 1c3cbb71e89f2b2249c11f6042ea8bf034e3d4da
            Reverse Dependencies: mesa wayland perl-XML-Parser fontconfig dbus expat-docs gdb git polkit python3 expat-32bit expat-pages cmake python dbus-glib expat-devel

            "expat" package is not found in source repositories.
