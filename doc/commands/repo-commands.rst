.. -*- coding: utf-8 -*-

==============================
Managing Repositories in INARY
==============================

inary package manager can download binary packages from repositories on local and remote \
servers. It allows adding and removing package repositories with a few commands.

.. note:: Repository operations needs privileges and can be allowed by only super user.


**Adding Repository**
---------------------

Adding a repository in system making with `inary add-repo` command


.. note:: Repository url can be a file path.

**Options**
^^^^^^^^^^^

add-repo options:
          --ignore-check               Ignore repository distribution check
          --no-fetch                   Does not fetch repository index and does not check distribution match
          --at                         Add repository at given position (0 is first)

.. note: --at option can not effective now.

**Using**
^^^^^^^^^

.. code-block:: shell

          sh ~$ inary add-repo <repository-name> <repository-url>
          sh ~$ inary ar <repository-name> <repository-url>

**Hints**
^^^^^^^^^

* GPG key check is performed during the repository addition. This check action can be by-passed, if not bypass, the added repository will be deactivated


**Removing Repository**
-----------------------

Removing a repository in system making with `inary remove-repo` command

**Using**
^^^^^^^^^

.. code-block:: shell

          sh ~$ inary remove-repo <repository-name>
          sh ~$ inary rr <repository-name>


**Update Repository**
---------------------

Refreshing the repository informations can be made with `inary update-repo` command. \
It synchronizes repository information whether index's sha1sum has changed.

**Options**
^^^^^^^^^^^

update-repo options:
          --f, --force               Update database in any case

**Using**
^^^^^^^^^
`update-repo` operation refreshes given repositor(y/ies) if the argument is given...

.. code-block:: shell

          sh ~$ inary update-repo <repository-name>
          sh ~$ inary ur <repository-name>

...but refreshes all repositories if no argument is given.

.. code-block:: shell

          sh ~$ inary update-repo
          sh ~$ inary ur

**Hints**
^^^^^^^^^
* GPG key checking is also making when this process is happened. So, if you won't confirm to pass this check action your updated repository will be deactivated.
* Disable repositories will not updated unless otherwise specified.

**Changing Activity of a Repository**
-------------------------------------

There are two types of repository in the system:
* Enable Repositories: added repositories are enabled by default.
* Disable Repositories: if a GPG key error is occurred while adding/updating a repository, or, if the user requests this, the repositories are deactivated.

**Enabling Repository**
^^^^^^^^^^^^^^^^^^^^^^^

`inary enable-repo` command is used to activate a repository which has already deactivated.


.. code-block:: shell

          sh ~$ inary enable-repo <repository-name>
          sh ~$ inary er <repository-name>

**Disabling Repository**
^^^^^^^^^^^^^^^^^^^^^^^^

`inary disable-repo` command is used to deactivate a repository.


.. code-block:: shell

          sh ~$ inary disable-repo <repository-name>
          sh ~$ inary dr <repository-name>
