.. -*- coding: utf-8 -*-

===========
inary check
===========

`inary check`  command performs a detailed analysis of the packages installed in the system. \
If there is content that is broken or deleted, or a modified config file, it allows us to see.

**Using**
---------
`check` command analyze only the named package if the argument is given...

.. code-block:: shell

          sh ~$ inary check <package-name>

...but analyzes all system if no argument is given.

.. code-block:: shell

          sh ~$ inary check


**Options**
--------------
check options:
            -c, --component              Check installed packages under given component.
            --config                     Checks only changed config files of the packages.


**Example Runtime Output**
--------------------------

.. code-block:: shell

        sh ~$ inary check
        Checking integrity of "acl"        OK
        Checking integrity of "bash"       OK
        Checking integrity of "unzip"      OK
        Checking integrity of "tar"        OK

        sh ~$ inary check acl
        Checking integrity of "acl"        OK
