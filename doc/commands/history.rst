.. -*- coding: utf-8 -*-

=============
inary history
=============

`inary history` command allows us to list the commands made in the past, undo \
changes made after a certain time (takeback), and create a system restore \
point (snapshot).
Basically it is inary's transactional history manager.

**Using**
---------

.. code-block:: shell

            sh ~$ inary hs
            sh ~$ inary history

**Options**
-----------

history options:
           -l, --last                  Output only the last 'n' operations.
           -s, --snapshot              Take snapshot of the current system.
           -t, --takeback              Takeback to the state after the given operation finished.


**Hints**
---------

`history` operation is not used to display only historical operations. This allows \
us to roll back operations or create a restore point at a time whenever user want.

.. note: Transactinal process will be specified in package processes.

.. note:: snapshot and takeback operations needs privileges and can be allowed by only super user.


**Example Runtime Output**
--------------------------

.. code-block:: shell

            sh ~$ inary history
            Inary Transactional History:
            Operation #1: repository update:
            Date: 2019-10-06 14:10
                * trykl
