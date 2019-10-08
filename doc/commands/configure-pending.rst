.. -*- coding: utf-8 -*-

=======================
inary configure-pending
=======================

`inary configure-pending` is used to complete the post-install scripts of packages installed on the system, \
but did not process the scripts after installation

.. note:: This operation needs privileges and can be allowed by only super user.

**Using**
---------

`configure-pending` operation configures only the named package if the argument is given...

.. code-block:: shell

          sh ~# inary configure-pending <package-name>
          sh ~# inary cp <package-name>

...but executes post-install scripts for all pending packages if no argument is given

.. code-block:: shell

          sh ~# inary configure-pending
          sh ~# inary cp



**Example Runtime Output**
--------------------------

.. code-block:: shell

        sh ~# inary configure-pending acl bash unzip gcc binutils tar
        Configuring "acl".
        Configuring "acl" package.
        Configured "acl".
        Configuring "bash".
        Configuring "bash" package.
        Configured "bash".
        Configuring "unzip".
        Configuring "unzip" package.
        Configured "unzip".
        Configuring "tar".
        Configuring "tar" package.
        Configured "tar".
