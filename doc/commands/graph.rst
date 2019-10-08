.. -*- coding: utf-8 -*-

===========
inary graph
===========

`inary graph` command draws the dependency graphic between the repositories attached to the system and creates an dot file.

**Output**
----------

graph options:
            -r, --repository            Specify a particular repository.
            -i, --installed             Graph of installed packages
            --ignore-installed          Do not show installed packages.
            -R, --reverse               Draw reverse dependency graph.
            -o, --output                Dot output file


**Example Runtime Output**
--------------------------

.. code-block:: shell

            sh ~$ inary graph
            Plotting a graph of relations among all repository packages.
