.. -*- coding: utf-8 -*-

=====================
Repository Operations
=====================

What is repository? 
-------------------

With its simple definition, package repositories consist of binary and source packages. These repositories make \
it easy to build dependency trees and manage packages. Repositories for inary are listed on our site. Let's \
start with adding any of these repositories. 

How to add a repository?
------------------------

.. code-block:: shell

          sh ~# inary ar try_repo https://master.dl.sourceforge.net/project/sulinos/SulinRepository/inary-index.xml
          Repository "try_repo" added to system.
          Updating package repository: "try_repo"
          Package database updated.

How do I know which repository to add?
--------------------------------------

I said that the repositories are divided into two. Binary warehouses contain ready-made packages. If you are a \
normal user, you can continue your life without using another warehouse, as we share on our site.
Source repositories require build from scratch. I will explain later how to do it.

How do I update repositories?
-----------------------------

As new packages are added, the package catalog of the warehouse is renewed. Following the changes from the \
renewed package catalog is the most important job of a package manager. For this reason, we want the user to \
do it manually. We don't have a command for this ...

Just joke :smile:... The command is this:

.. code-block:: shell

          sh ~# inary ur try_repo 
          Updating package repository: "try_repo"
          Package database updated.

If you need update all repositories same time.

.. code-block:: shell

          sh ~# inary ur  
          Updating package repository: "try_repo"
          Updating package repository: "source_repo"
          Updating package repository: "local_repo"
          Package database updated.

How to list the repositories?
-----------------------------

.. code-block:: shell

          sh ~# inary lr 
          try_repo [active]
             https://master.dl.sourceforge.net/project/sulinos/SulinRepository/inary-index.xml
          source_repo [inactive]
             https://gitlab.com/sulinos/repositories/SulinRepository/-/raw/master/inary-index.xml

What can I do to fiddling repositories?
---------------------------------------

In other package management systems, you are asked to download tons of data every time you update your \
repositories. Sometimes the warehouse we have installed to add a package can be a lot of trouble. At this \
stage, inary offers two options. Either you delete the repository forever (or until your pleasure re-adds), \
or keep it in your system and deactive it. In this case, the deactive repo is not included in the package \
lists as if it were removed from the system until you activate it or remove it. \
That is, you can keep this repositories away from package management by preserving the commodity. \
Sometimes the package management system does this automatically. As soon as repos that are incompatible \
with your distro are added, they are deactive so preserving your system to broken and uncompitable packages.

Disabling Repository
^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

          sh ~# inary dr try_repo   

This command does not output, but you already know how to check the repository list: joy:

.. code-block:: shell

          sh ~# inary lr 
          try_repo [inactive]
             https://master.dl.sourceforge.net/project/sulinos/SulinRepository/inary-index.xml

Removing Repository
^^^^^^^^^^^^^^^^^^^

.. warning:: this process may be destructive for your repo list. Please not forget your repo link or back up it

.. code-block:: shell

          sh ~# inary rr try_repo 
          Repository "try_repo" removed from system.

Enabling Repository
^^^^^^^^^^^^^^^^^^^^
Let's say we needed a warehouse that was disable later, then it will disappear. That's when you'll have to get it back.

.. note:: It will take long time. And you will wait without any output.

.. code-block:: shell

          sh ~# inary er try_repo   

